"""Mercado con régimen causal: el driver de precios es conocido por construcción (ground truth)."""
import numpy as np

FEATURES = ["momentum", "spread", "volume", "news", "orderflow", "sentiment"]
REGIMES = ["momentum", "news"]  # driver causal del régimen

class Market:
    def __init__(self, seed=0, n_agents=8, ticks=40, regime="news", lam=0.03, switch_at=None):
        if isinstance(switch_at, list):
            self.switch_ats = sorted(switch_at)
        elif switch_at is None:
            self.switch_ats = []
        else:
            self.switch_ats = [switch_at]
        self.rng = np.random.default_rng(seed)
        self.n_agents = n_agents
        self.ticks = ticks
        self.regime = regime
        self.regime_initial = regime
        self.lam = lam
        self.P = 100.0
        self.history = {"price": [self.P], "returns": [0.0], "features": [], "regimes": [], "vol": 1.0}

    def _features(self, t):
        """Features del tick t; solo el driver del régimen entra directamente en los retornos."""
        self.regime = self.regime_at(t)
        driver = self.rng.normal(0, 1.0)  # señal causal ~ N(0,1)
        momentum = float(driver + self.rng.normal(0, 0.7)) if self.regime == "momentum" else float(self.rng.normal(0, 0.7))
        news = float(driver + self.rng.normal(0, 0.7)) if self.regime == "news" else float(self.rng.normal(0, 0.7))
        # volumen con leve señal propia (no causal en el régimen)
        volume = float(1.0 + 0.3 * self.rng.normal(0, 1.0))
        # Distractores no causales: orderflow correlaciona con momentum y sentiment con news;
        # por tanto, cada uno correlaciona con el driver cuando su régimen correspondiente está activo.
        orderflow = float(momentum * 0.3 + self.rng.normal(0, 0.6))
        sentiment = float(news * 0.3 + self.rng.normal(0, 0.6))
        spread = float(self.rng.uniform(0.004, 0.03))
        feats = {"momentum": round(momentum, 3), "spread": round(spread, 4),
                 "volume": round(volume, 3), "news": round(news, 3),
                 "orderflow": round(orderflow, 3), "sentiment": round(sentiment, 3)}
        self.history["features"].append(feats)
        self.history["regimes"].append(self.regime)
        return feats

    def _fundamental_return(self, features):
        """Retorno fundamental: solo el driver causal importa."""
        if self.regime == "momentum":
            return 0.02 * features["momentum"]
        else:
            return 0.02 * features["news"]

    def step(self, orders):
        """Actualiza precio: retorno fundamental (régimen) + imbalance + ruido."""
        raw = sum((1 if a == "buy" else -1) * s for _, a, s in orders)
        imbalance = raw / (self.n_agents * 5.0)
        feat = self.history["features"][-1]
        ret = self.lam * imbalance + self._fundamental_return(feat) + self.rng.normal(0, 0.005)
        self.P = max(50.0, self.P * (1 + ret))
        self.history["price"].append(self.P)
        self.history["returns"].append(ret)
        return ret

    def recent_history(self, k=4):
        """Últimos k ticks: features + retorno (para que el agente infiera el driver)."""
        rows = []
        for i in range(max(1, len(self.history["features"]) - k + 1), len(self.history["features"]) + 1):
            if i - 1 < len(self.history["features"]) and i < len(self.history["returns"]):
                rows.append((self.history["features"][i - 1], self.history["returns"][i]))
        return rows

    def regime_at(self, t):
        """Régimen efectivo en el tick t (tras posibles switches)."""
        regime = self.regime_initial
        for s in self.switch_ats:
            if t >= s:
                regime = "momentum" if regime == "news" else "news"
        return regime
