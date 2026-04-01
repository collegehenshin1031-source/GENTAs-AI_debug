import os
import json
import time
import random
import pickle
from datetime import datetime
import hagetaka_scanner as scanner
import fair_value_calc_y4 as fv

# キャッシュ保存先
CACHE_DIR = "data"
MA_CACHE_FILE = os.path.join(CACHE_DIR, "daily_ma_cache.json")
HAGETAKA_CACHE_FILE = os.path.join(CACHE_DIR, "daily_hagetaka_cache.pkl")
TEMP_MA_FILE = os.path.join(CACHE_DIR, "daily_ma_cache_temp.json")
TEMP_HAGETAKA_FILE = os.path.join(CACHE_DIR, "daily_hagetaka_cache_temp.pkl")

def run_nightly_batch():
    print(f"[{datetime.now()}] 夜間バッチ処理（全銘柄キャッシュ生成）を開始します")
    
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        
    all_codes = scanner.get_all_japan_stocks()
    total = len(all_codes)
    
    # ----------------------------------------------------
    # 1. Tab2（M&A予兆監視）用データの生成（JSON保存）
    # ----------------------------------------------------
    print(f"\n[{datetime.now()}] 1/2: M&Aスコア用データの取得を開始")
    ma_results = {}
    chunk_size = 50
    for i in range(0, total, chunk_size):
        chunk_codes = all_codes[i:i+chunk_size]
        try:
            bundle_data = fv.calc_genta_bundle(chunk_codes)
            ma_results.update(bundle_data)
        except Exception as e:
            print(f"M&Aデータ取得エラー: {e}")
            
        time.sleep(random.uniform(2.0, 5.0))
        
    with open(TEMP_MA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "data": ma_results}, f, ensure_ascii=False)
        
    # ----------------------------------------------------
    # 2. Tab1（ハゲタカスコープ）用データの生成（Pickle保存）
    # ----------------------------------------------------
    print(f"\n[{datetime.now()}] 2/2: ハゲタカシグナル用データのスキャンを開始")
    
    def dummy_progress(current, total_count, text):
        if current % 100 == 0 or current == total_count:
            print(f"スキャン進捗: {current}/{total_count} - {text}")
            
    # ここで全銘柄の重いスキャン処理をサーバー側で代行
    hagetaka_results = scanner.scan_all_stocks(all_codes, progress_callback=dummy_progress)
    
    with open(TEMP_HAGETAKA_FILE, 'wb') as f:
        pickle.dump(hagetaka_results, f)
        
    # ----------------------------------------------------
    # 3. アトミック置換（完成データを一瞬ですり替え）
    # ----------------------------------------------------
    os.replace(TEMP_MA_FILE, MA_CACHE_FILE)
    os.replace(TEMP_HAGETAKA_FILE, HAGETAKA_CACHE_FILE)
    print(f"\n[{datetime.now()}] 夜間バッチ処理完了。すべてのキャッシュを最新に更新しました。")

if __name__ == "__main__":
    run_nightly_batch()
