import time
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

class SignalLevel(Enum):
    LOCKON = "🔴 ロックオン"
    HIGH = "🟠 高警戒"
    MEDIUM = "🟡 監視中"
    LOW = "🟢 平常"

class ScanMode(Enum):
    QUICK = "quick"
    PRIME = "prime"
    STANDARD = "standard"
    GROWTH = "growth"
    ALL = "all"
    CUSTOM = "custom"

@dataclass
class ScanOption:
    mode: ScanMode
    label: str
    description: str
    estimated_count: int
    estimated_time: str
    warning: Optional[str] = None

SCAN_OPTIONS = {
    ScanMode.QUICK: ScanOption(ScanMode.QUICK, "⚡ クイックスキャン", "主要銘柄100社", 100, "1-2分"),
    ScanMode.PRIME: ScanOption(ScanMode.PRIME, "🏢 プライム市場", "東証プライム", 1800, "10-15分"),
    ScanMode.STANDARD: ScanOption(ScanMode.STANDARD, "🏬 スタンダード市場", "東証スタンダード", 1400, "8-12分"),
    ScanMode.GROWTH: ScanOption(ScanMode.GROWTH, "🌱 グロース市場", "東証グロース", 500, "3-5分"),
    ScanMode.ALL: ScanOption(ScanMode.ALL, "🌐 全銘柄スキャン", "日本株全銘柄", 4000, "20-30分"),
    ScanMode.CUSTOM: ScanOption(ScanMode.CUSTOM, "✏️ 銘柄コード直接入力", "指定銘柄のみ", 0, "入力数による"),
}

@dataclass
class HagetakaSignal:
    code: str
    name: str
    signal_level: SignalLevel
    total_score: int
    stealth_score: int = 0
    board_score: int = 0
    volume_score: int = 0
    bonus_score: int = 0
    signals: List[str] = field(default_factory=list)
    price: float = 0
    change_pct: float = 0
    volume: int = 0
    avg_volume: int = 0
    volume_ratio: float = 0
    turnover_pct: float = 0
    market_cap: float = 0
    trading_value: float = 0
    detected_at: datetime = field(default_factory=datetime.now)

def get_stock_data(code: str) -> Optional[Dict[str, Any]]:
    try:
        ticker = yf.Ticker(f"{code}.T")
        hist = ticker.history(period="1mo")
        if hist.empty or len(hist) < 5: return None
        info = ticker.info
        latest = hist.iloc[-1]
        prev = hist.iloc[-2]
        current_volume = int(latest['Volume'])
        avg_vol = int(hist['Volume'].mean())
        return {
            "code": code,
            "name": info.get('shortName', code),
            "price": float(latest['Close']),
            "change_pct": ((latest['Close'] - prev['Close']) / prev['Close'] * 100),
            "volume": current_volume,
            "avg_volume_20d": avg_vol,
            "volume_ratio": current_volume / avg_vol if avg_vol > 0 else 1,
            "market_cap": info.get('marketCap', 0),
            "trading_value": float(latest['Close']) * current_volume,
            "hist": hist
        }
    except: return None

def analyze_hagetaka_signal(data: Dict[str, Any]) -> HagetakaSignal:
    score = 0
    signals = []
    vol_ratio = data.get("volume_ratio", 0)
    if vol_ratio > 2:
        score += 40
        signals.append("🔥 出来高急増")
    elif vol_ratio > 1.5:
        score += 20
        signals.append("📈 出来高増加")
        
    level = SignalLevel.LOW
    if score >= 60: level = SignalLevel.LOCKON
    elif score >= 40: level = SignalLevel.HIGH
    elif score >= 20: level = SignalLevel.MEDIUM
    
    return HagetakaSignal(
        code=data['code'], name=data['name'], signal_level=level,
        total_score=score, signals=signals, price=data['price'],
        change_pct=data['change_pct'], volume=data['volume'],
        volume_ratio=vol_ratio, market_cap=data['market_cap']
    )

def scan_all_stocks(codes: List[str], progress_callback=None) -> List[HagetakaSignal]:
    results = []
    total = len(codes)
    for i, code in enumerate(codes):
        data = get_stock_data(code)
        if data:
            results.append(analyze_hagetaka_signal(data))
        if progress_callback:
            progress_callback(i + 1, total, code)
    results.sort(key=lambda x: x.total_score, reverse=True)
    return results

def get_all_japan_stocks() -> List[str]:
    # 簡易版の主要銘柄リスト
    return ["7203", "9984", "6758", "8306", "9432", "6861", "7267", "4502", "6501", "8058"]

def get_scan_targets(mode: ScanMode, custom_codes=None) -> List[str]:
    if mode == ScanMode.CUSTOM: return custom_codes or []
    return get_all_japan_stocks()

def get_volume_ranking_stocks(n=100):
    return get_all_japan_stocks()
