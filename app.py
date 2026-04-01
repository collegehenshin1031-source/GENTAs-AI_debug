"""
源太AI🤖ハゲタカSCOPE
- 生徒配布用・完全オフライン究極安定版
- 全銘柄24時間監視
- ハゲタカ（機関投資家）の足跡を自動検知
- ロックオン通知システム
"""

import re
import unicodedata
import time
import os
import pickle
import json
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

import hagetaka_scanner as scanner
import ma_detector as ma
import notifier

# ==========================================
# 🔑 パスワード設定
# ==========================================
LOGIN_PASSWORD = "88888"
ADMIN_CODE = "888888"

# ==========================================
# UI設定
# ==========================================
st.set_page_config(
    page_title="源太AI🤖ハゲタカSCOPE", 
    page_icon="🦅", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🎨 先乗り株カレッジ ブランドCSS (完全保持)
# ==========================================
st.markdown("""
<style>
/* 基本設定・Streamlit要素非表示 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}

/* 全体背景 */
div[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #FAFAFA 0%, #FFF5F5 100%) !important;
}

/* メインコンテナ */
.main .block-container {
    max-width: 1200px !important;
    padding: 1rem 2rem 3rem 2rem !important;
    margin: 0 auto !important;
}

/* ヘッダー */
h1 {
    text-align: center !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #C41E3A 0%, #E85A71 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 0.5rem !important;
}

/* サブタイトル */
.subtitle {
    text-align: center;
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

/* タブスタイル */
.stTabs [data-baseweb="tab-list"] {
    justify-content: center !important;
    gap: 0 !important;
    background-color: #FFF !important;
    padding: 0.4rem !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 12px rgba(196, 30, 58, 0.1) !important;
    margin-bottom: 1.5rem !important;
}

.stTabs [data-baseweb="tab"] {
    padding: 0.75rem 2rem !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    color: #666 !important;
    transition: all 0.3s ease !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #C41E3A 0%, #E85A71 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3) !important;
}

.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ボタン */
div.stButton {
    text-align: center !important;
}

div.stButton > button:first-child {
    background: linear-gradient(135deg, #C41E3A 0%, #E85A71 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.85rem 2.5rem !important;
    box-shadow: 0 4px 15px rgba(196, 30, 58, 0.25) !important;
    transition: all 0.3s ease !important;
    font-size: 1.05rem !important;
}

div.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(196, 30, 58, 0.35) !important;
}

/* カード */
.stock-card {
    background: white;
    border-radius: 16px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 5px solid #C41E3A;
    transition: all 0.2s ease;
}

.stock-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(196, 30, 58, 0.15);
}

.stock-card.lockon {
    border-left-color: #C41E3A;
    background: linear-gradient(135deg, #FFF 0%, #FFF5F5 100%);
}

.stock-card.high {
    border-left-color: #F97316;
    background: linear-gradient(135deg, #FFF 0%, #FFF7ED 100%);
}

.stock-card.medium {
    border-left-color: #EAB308;
    background: linear-gradient(135deg, #FFF 0%, #FEFCE8 100%);
}

/* スコアバッジ */
.score-badge {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.9rem;
}

.score-badge.lockon {
    background: linear-gradient(135deg, #C41E3A 0%, #E85A71 100%);
    color: white;
}

.score-badge.high {
    background: linear-gradient(135deg, #F97316 0%, #FB923C 100%);
    color: white;
}

.score-badge.medium {
    background: linear-gradient(135deg, #EAB308 0%, #FACC15 100%);
    color: #1a1a1a;
}

/* シグナルタグ */
.signal-tag {
    display: inline-block;
    background: #F3F4F6;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-size: 0.8rem;
    margin: 0.15rem;
    color: #374151;
}

/* メトリクス */
[data-testid="stMetric"] {
    background: white !important;
    padding: 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #C41E3A !important;
}

/* Expander */
.stExpander {
    background-color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}

/* 入力フォーム */
.stTextArea textarea, .stTextInput input {
    border-radius: 10px !important;
    border: 2px solid #E8E8E8 !important;
    font-size: 16px !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #C41E3A !important;
}

/* ヒーローセクション */
.hero-section {
    text-align: center;
    padding: 2rem 1rem;
    background: linear-gradient(135deg, #C41E3A 0%, #E85A71 100%);
    border-radius: 20px;
    color: white;
    margin-bottom: 1.5rem;
}

.hero-section h2 {
    color: white !important;
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
}

.hero-section p {
    opacity: 0.9;
    font-size: 0.95rem;
}

/* ステータスインジケーター */
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: white;
    border-radius: 20px;
    font-size: 0.85rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

.status-dot.active {
    background: #22C55E;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* レスポンシブ */
@media (max-width: 768px) {
    .main .block-container {
        padding: 0.75rem 1rem 2rem 1rem !important;
    }
    h1 {
        font-size: 1.5rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.6rem 1rem !important;
        font-size: 0.9rem !important;
        white-space: nowrap !important;
    }
    div.stButton > button:first-child {
        width: 100% !important;
    }
    .hero-section {
        padding: 1.5rem 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 認証（フォーム化による高速ログイン）
# ==========================================
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        
    if not st.session_state["logged_in"]:
        st.markdown("## 🔒 ACCESS RESTRICTED")
        with st.form("login_form"):
            password_input = st.text_input("パスワードを入力してください", type="password")
            submit_btn = st.form_submit_button("ログイン")
            
            if submit_btn:
                input_norm = unicodedata.normalize('NFKC', password_input).upper().strip()
                secret_norm = unicodedata.normalize('NFKC', LOGIN_PASSWORD).upper().strip()
                if input_norm == secret_norm:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("パスワードが違います 🙅")
        st.stop()

check_password()


# ==========================================
# ヘルパー関数
# ==========================================
def fmt_price(x):
    if x is None or pd.isna(x): return "—"
    try: return f"¥{float(x):,.0f}"
    except: return "—"

def fmt_pct(x):
    if x is None or pd.isna(x): return "—"
    try:
        v = float(x)
        sign = "+" if v >= 0 else ""
        return f"{sign}{v:.2f}%"
    except: return "—"

def fmt_volume(x):
    if x is None or pd.isna(x): return "—"
    try:
        v = int(x)
        if v >= 1e6: return f"{v/1e6:.1f}M"
        if v >= 1e3: return f"{v/1e3:.0f}K"
        return str(v)
    except: return "—"

def fmt_market_cap(x):
    if x is None or pd.isna(x) or x == 0: return "—"
    try:
        v = float(x) / 1e8  # 億円換算
        if v >= 10000: return f"{v/10000:.1f}兆円"
        return f"{v:.0f}億円"
    except: return "—"

def get_signal_class(signal_level):
    if signal_level == scanner.SignalLevel.LOCKON:
        return "lockon"
    elif signal_level == scanner.SignalLevel.HIGH:
        return "high"
    else:
        return "medium"

def render_stock_card(signal: scanner.HagetakaSignal):
    """銘柄カードをレンダリング（デザイン完全保持）"""
    card_class = get_signal_class(signal.signal_level)
    badge_class = card_class
    
    st.markdown(f"""
    <div class="stock-card {card_class}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <span class="score-badge {badge_class}">{signal.signal_level.value}</span>
                <span style="font-size: 1.3rem; font-weight: 700; margin-left: 0.5rem;">{signal.name}</span>
                <span style="color: #666; margin-left: 0.5rem;">({signal.code})</span>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.4rem; font-weight: 700;">{fmt_price(signal.price)}</div>
                <div style="color: {'#22C55E' if signal.change_pct >= 0 else '#EF4444'}; font-weight: 600;">
                    {fmt_pct(signal.change_pct)}
                </div>
            </div>
        </div>
        <div style="margin-top: 0.75rem; display: flex; gap: 1.5rem; flex-wrap: wrap; font-size: 0.9rem; color: #666;">
            <span>📊 スコア: <strong style="color: #C41E3A;">{signal.total_score}点</strong></span>
            <span>📈 出来高倍率: <strong>{getattr(signal, 'volume_ratio', 0):.1f}倍</strong></span>
            <span>🌪️ 回転率: <strong>{getattr(signal, 'turnover_pct', 0):.1f}%</strong></span>
            <span>💰 時価総額: <strong>{fmt_market_cap(getattr(signal, 'market_cap', 0))}</strong></span>
        </div>
        <div style="margin-top: 0.75rem;">
            {''.join([f'<span class="signal-tag">{s}</span>' for s in getattr(signal, 'signals', [])[:5]])}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 通知設定初期化
# ==========================================
def init_session_state():
    if "notification_config" not in st.session_state:
        st.session_state["notification_config"] = notifier.load_notification_config()
    if "watchlist" not in st.session_state:
        st.session_state["watchlist"] = notifier.load_watchlist()
    if "scan_results" not in st.session_state:
        st.session_state["scan_results"] = []
    if "last_scan_time" not in st.session_state:
        st.session_state["last_scan_time"] = None

init_session_state()


# ==========================================
# メイン画面
# ==========================================
st.title("🦅 源太AI ハゲタカSCOPE")
st.markdown('<p class="subtitle">プロの投資戦略をのぞき見る「カンニング級の裏・攻略本」</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎯 ロックオン銘柄", "📊 ハゲタカ監視", "🔔 通知設定"])

# ==========================================
# タブ1: ロックオン銘柄（完全オフライン キャッシュ読込）
# ==========================================
with tab1:
    st.markdown("""
    <div class="hero-section">
        <h2>🎯 AIが検知した「今日の標的」</h2>
        <p>夜間にAIが全銘柄をスキャンした最新データです</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        last_scan = st.session_state.get("last_scan_time")
        if last_scan:
            st.markdown(f"""
            <div class="status-indicator">
                <span class="status-dot active"></span>
                最終データ読込: {last_scan.strftime('%H:%M')}
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        lockons = [s for s in st.session_state.get("scan_results", []) if getattr(s, 'total_score', 0) >= 50]
        st.metric("ロックオン銘柄", f"{len(lockons)}件")
    
    st.divider()
    st.markdown("### 🔍 表示データ設定")
    
    scan_mode_options = {
        "⚡ クイックスキャン（推奨）": scanner.ScanMode.QUICK,
        "🌱 グロース市場（約500銘柄）": scanner.ScanMode.GROWTH,
        "🏬 スタンダード市場（約1,400銘柄）": scanner.ScanMode.STANDARD,
        "🏢 プライム市場（約1,800銘柄）": scanner.ScanMode.PRIME,
        "🌐 全銘柄表示（約3,800銘柄）": scanner.ScanMode.ALL,
        "✏️ 銘柄コードを直接入力": scanner.ScanMode.CUSTOM,
    }
    
    selected_mode_label = st.selectbox("表示対象を選択", options=list(scan_mode_options.keys()), index=0)
    selected_mode = scan_mode_options[selected_mode_label]
    scan_option = scanner.SCAN_OPTIONS[selected_mode]
    
    info_col1, info_col2 = st.columns([2, 1])
    with info_col1:
        st.markdown(f"""
        <div style="background: #F8F9FA; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.9rem;">
            📋 <strong>{scan_option.description}</strong><br>
            <span style="color: #666;">※夜間に自動構築されたキャッシュデータから瞬時に呼び出します</span>
        </div>
        """, unsafe_allow_html=True)
    
    custom_codes = []
    if selected_mode == scanner.ScanMode.CUSTOM:
        custom_input = st.text_input("銘柄コードを入力（スペース区切り）", placeholder="例: 7203 9984 6758 8306")
        if custom_input:
            custom_codes = [c.strip() for c in custom_input.split() if c.strip()]
            st.info(f"📝 {len(custom_codes)}銘柄を入力済み")
    
    st.markdown("") 
    scan_btn = st.button("🚀 データ呼び出し", type="primary", use_container_width=True)
    
    if scan_btn:
        codes = scanner.get_scan_targets(selected_mode, custom_codes)
        cache_path = "data/daily_hagetaka_cache.pkl"
        
        # 【絶対防御】ファイルが存在する場合のみ読み込む
        if os.path.exists(cache_path):
            with st.spinner("📦 データを読み込み中..."):
                try:
                    with open(cache_path, 'rb') as f:
                        all_results = pickle.load(f)
                    
                    if selected_mode == scanner.ScanMode.ALL:
                        results = all_results
                    else:
                        target_set = set(codes)
                        results = [r for r in all_results if r.code in target_set]
                        
                    if results:
                        st.session_state["scan_results"] = results
                        st.session_state["last_scan_time"] = datetime.now()
                        st.success(f"✅ {len(results)}件のデータを瞬時に読み込みました！")
                    else:
                        st.warning("⚠️ 指定された銘柄のデータがキャッシュ内にありませんでした。")
                        
                except Exception as e:
                    st.error(f"データの読み込みに失敗しました: {e}")
        else:
            st.warning("🔄 現在、サーバー裏側で最新データを構築中です。完了までしばらくお待ちください。")
            
        st.rerun()
    
    results = st.session_state.get("scan_results", [])
    
    if results:
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            min_score_filter = st.slider("最低スコア", 0, 100, 0, key="filter_score")
        with col2:
            sort_option = st.selectbox("並び順", ["スコア順", "出来高倍率順", "回転率順"])
        
        filtered = [s for s in results if s.total_score >= min_score_filter]
        
        if sort_option == "出来高倍率順":
            filtered.sort(key=lambda x: getattr(x, 'volume_ratio', 0), reverse=True)
        elif sort_option == "回転率順":
            filtered.sort(key=lambda x: getattr(x, 'turnover_pct', 0), reverse=True)
        else:
            filtered.sort(key=lambda x: getattr(x, 'total_score', 0), reverse=True)
        
        st.markdown(f"### 📋 厳選・監視リスト（表示上限20件）")
        
        if not filtered:
            st.info("条件に合致する銘柄がありません。フィルターを調整してください。")
        else:
            for signal in filtered[:20]:
                render_stock_card(signal)
                # 詳細展開（完全保持）
                with st.expander(f"📊 {signal.code} の詳細分析"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🥷 ステルス集積", f"{getattr(signal, 'stealth_score', 0)}/35点")
                    with col2:
                        st.metric("🧱 板の違和感", f"{getattr(signal, 'board_score', 0)}/35点")
                    with col3:
                        st.metric("🔥 出来高臨界点", f"{getattr(signal, 'volume_score', 0)}/30点")
                    with col4:
                        st.metric("🌟 ボーナス", f"+{getattr(signal, 'bonus_score', 0)}点")
                    
                    st.markdown("**検知シグナル:**")
                    for s in getattr(signal, 'signals', []):
                        st.markdown(f"- {s}")
    else:
        st.info("👆 「データ呼び出し」ボタンを押して、ハゲタカの足跡を表示してください。")
        
    st.divider()
    with st.expander("📚 ハゲタカスコープの仕組み"):
        st.markdown("""
        ### 🦅 3つの検知ロジック
        #### 1. 🥷 ステルス集積（最大35点）
        目立たないように株を買い集めている動きを検知します。
        #### 2. 🧱 板の違和感（最大35点）
        気配値（板）に現れる不自然な並びや歪みを検知します。
        #### 3. 🔥 出来高の臨界点（最大30点）
        爆発直前に見られる取引量の異常な変化を検知します。
        """)

# ==========================================
# タブ2: ハゲタカ監視（M&A予兆）完全オフライン版
# ==========================================
with tab2:
    st.markdown("""
    <div class="hero-section">
        <h2>📊 M&A予兆監視システム</h2>
        <p>TOB・完全子会社化・MBOなど、M&Aの可能性が高い銘柄を自動検知</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 監視リスト")
    watchlist = st.session_state.get("watchlist", [])
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_codes = st.text_input("銘柄を追加", placeholder="例: 7203 9984 6758", key="add_watch")
    with col2:
        if st.button("➕ 追加", key="add_watch_btn", use_container_width=True):
            if new_codes:
                new_list = [c.strip() for c in new_codes.split() if c.strip()]
                for code in new_list:
                    if code not in watchlist:
                        watchlist.append(code)
                st.session_state["watchlist"] = watchlist
                notifier.save_watchlist(watchlist)
                st.success(f"{len(new_list)}件追加しました")
                st.rerun()
    
    if watchlist:
        st.markdown(f"**現在の監視銘柄** ({len(watchlist)}件): {', '.join(watchlist)}")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔍 M&A分析実行", type="primary", key="ma_analyze"):
                with st.spinner("🎯 M&Aデータをキャッシュから展開中..."):
                    cache_path_ma = "data/daily_ma_cache.json"
                    bundle = {}
                    
                    if os.path.exists(cache_path_ma):
                        try:
                            with open(cache_path_ma, 'r', encoding='utf-8') as f:
                                cache_data = json.load(f)
                                all_bundle = cache_data.get("data", {})
                                bundle = {c: all_bundle[c] for c in watchlist if c in all_bundle}
                        except Exception as e:
                            st.error(f"キャッシュ読み込みエラー: {e}")
                    
                    if not bundle:
                        st.warning("⚠️ キャッシュデータが存在しないか、監視リストの銘柄がまだ裏側で処理されていません。\nデータ構築の完了をお待ちください。")
                    else:
                        stock_data_list = list(bundle.values())
                        # 【絶対防御】with_news=Falseにすることで、フロントエンドでのニューススクレイピング通信を完全停止
                        ma_results = ma.batch_analyze_ma(stock_data_list, with_news=False)
                        st.session_state["ma_results"] = ma_results
                        st.rerun()

        with col2:
            if st.button("🗑️ リストをクリア", key="clear_watch"):
                st.session_state["watchlist"] = []
                notifier.save_watchlist([])
                st.rerun()
        
        if "ma_results" in st.session_state and st.session_state["ma_results"]:
            st.divider()
            st.markdown("### 📊 M&A予兆分析結果")
            for score in st.session_state["ma_results"]:
                if score.signal_level == ma.MASignalLevel.CRITICAL:
                    card_class, badge_class = "lockon", "lockon"
                elif score.signal_level == ma.MASignalLevel.HIGH:
                    card_class, badge_class = "high", "high"
                else:
                    card_class, badge_class = "medium", "medium"
                
                st.markdown(f"""
                <div class="stock-card {card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span class="score-badge {badge_class}">{score.signal_level.value}</span>
                            <span style="font-size: 1.2rem; font-weight: 700; margin-left: 0.5rem;">{score.name}</span>
                            <span style="color: #666;">({score.code})</span>
                        </div>
                        <div style="font-size: 1.3rem; font-weight: 700; color: #C41E3A;">
                            {score.total_score}点
                        </div>
                    </div>
                    <div style="margin-top: 0.5rem;">
                        {''.join([f'<span class="signal-tag">{t}</span>' for t in score.reason_tags[:5]])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 詳細展開（完全保持）
                with st.expander(f"📋 {score.code} 詳細"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("ニュース", f"{score.news_score}/40")
                    col2.metric("出来高", f"{score.volume_score}/30")
                    col3.metric("バリュエーション", f"{score.valuation_score}/20")
                    col4.metric("テクニカル", f"{score.technical_score}/10")
    else:
        st.info("監視銘柄を追加してください。")


# ==========================================
# タブ3: 通知設定
# ==========================================
with tab3:
    st.markdown("""
    <div class="hero-section">
        <h2>🔔 ロックオン通知設定</h2>
        <p>条件合致の「標的」を検知した瞬間、スマホに通知が届きます</p>
    </div>
    """, unsafe_allow_html=True)
    
    config = st.session_state.get("notification_config", notifier.NotificationConfig())
    st.markdown("### ⚙️ 基本設定")
    enabled = st.toggle("通知を有効にする", value=config.enabled, key="notify_enabled")
    min_score = st.slider("通知する最低スコア", 0, 100, config.min_score_threshold, key="min_score")
    
    st.divider()
    st.markdown("### 📧 メール通知設定")
    email_enabled = st.toggle("メール通知を有効にする", value=config.email_enabled, key="email_enabled")
    
    if email_enabled:
        col1, col2 = st.columns(2)
        with col1:
            email_address = st.text_input("送信先メールアドレス", value=config.email_address, key="email_address")
            smtp_server = st.text_input("SMTPサーバー", value=config.smtp_server, key="smtp_server")
        with col2:
            smtp_user = st.text_input("SMTPユーザー", value=config.smtp_user, key="smtp_user")
            smtp_password = st.text_input("SMTPパスワード", value=config.smtp_password, type="password", key="smtp_password")
        
        smtp_port = st.number_input("SMTPポート", value=config.smtp_port, key="smtp_port")
        
        if email_address and smtp_user and smtp_password:
            if st.button("📧 テスト送信", key="test_email"):
                result = notifier.send_email(
                    to_address=email_address, subject="🎯 ハゲタカSCOPE テスト通知",
                    body="ロックオン通知のテストです。\n\n設定が正常に機能しています。",
                    smtp_server=smtp_server, smtp_port=int(smtp_port),
                    smtp_user=smtp_user, smtp_password=smtp_password
                )
                if result.success: st.success("✅ テスト送信成功！")
                else: st.error(f"❌ {result.message}")
    else:
        email_address = config.email_address
        smtp_server = config.smtp_server
        smtp_user = config.smtp_user
        smtp_password = config.smtp_password
        smtp_port = config.smtp_port
    
    st.divider()
    if st.button("💾 設定を保存", type="primary", key="save_config"):
        new_config = notifier.NotificationConfig(
            enabled=enabled, email_enabled=email_enabled,
            email_address=email_address if email_enabled else config.email_address,
            smtp_server=smtp_server if email_enabled else config.smtp_server,
            smtp_port=int(smtp_port) if email_enabled else config.smtp_port,
            smtp_user=smtp_user if email_enabled else config.smtp_user,
            smtp_password=smtp_password if email_enabled else config.smtp_password,
            line_enabled=False, line_token="", min_score_threshold=min_score, notify_critical_only=False,
        )
        notifier.save_notification_config(new_config)
        st.session_state["notification_config"] = new_config
        st.success("✅ 設定を保存しました！")


# ==========================================
# フッター・管理者メニュー
# ==========================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.85rem; padding: 1rem;">
    ⚠️ 投資は自己責任でお願いします。本ツールは情報提供を目的としており、投資助言ではありません。<br>
    © フヤセル - 源太AI ハゲタカSCOPE
</div>
""", unsafe_allow_html=True)

with st.expander("🔧 管理者メニュー"):
    admin_input = st.text_input("管理者コード", type="password", key="admin_pass")
    if admin_input == ADMIN_CODE:
        st.success("認証OK")
        if st.button("🗑️ キャッシュ削除"):
            st.cache_data.clear()
            st.success("削除完了！")
            time.sleep(1)
            st.rerun()
