"""
Core recommendation engine for MoodPlay Phi.
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np

# ---------- Data Schemas ----------

@dataclass
class Item:
    id: str
    title: str
    type: str                   # "film"/"serie"/"doc"/"podcast"/"clip"
    genres: List[str]
    moods: List[str]
    duration_min: float
    region_tags: List[str]
    embedding: np.ndarray       # E_i in R^d
    facet: Tuple[int, int]      # (format_bucket_id, mood_bucket_id)

@dataclass
class UserState:
    g: np.ndarray               # taste vector in R^d
    R: np.ndarray               # KxK rhythm transition matrix
    C: float                    # comfort account
    N: float                    # novelty debt account
    exposure: Dict[str, float]  # item_id -> recent exposure weight
    last_facet: int             # last state index (for rhythm)
    z: np.ndarray               # last context latent

@dataclass
class ContextSignals:
    hour: int
    day_of_week: int            # 0=Mon..6=Sun (your choice)
    weather: str                # "soleil"/"pluie"/"nuage"/...
    city: str
    with_friends: bool
    device: str                 # "mobile"/"tv"/"desktop"
    # optional additional signals...

# ---------- Constants ----------

FORMAT_BUCKETS = [(0,30), (31,60), (61,10_000)]   # court, moyen, long
MOOD_BUCKETS = ["cosy", "inspirant", "énergique", "contemplatif"]
K = len(FORMAT_BUCKETS) * len(MOOD_BUCKETS)

# ---------- Core Functions ----------

def facet_index(fmt_id: int, mood_id: int) -> int:
    """Convert format and mood indices to a single facet index."""
    return fmt_id * len(MOOD_BUCKETS) + mood_id

def minutes_bucket(m: float) -> int:
    """Convert duration in minutes to format bucket index."""
    for idx, (lo, hi) in enumerate(FORMAT_BUCKETS):
        if lo <= m <= hi:
            return idx
    return len(FORMAT_BUCKETS) - 1

class MoodPlayEngine:
    """Main recommendation engine class implementing the MoodPlay Phi algorithm."""
    
    def __init__(self, embedding_dim: int = 64):
        """
        Initialize the recommendation engine.
        
        Args:
            embedding_dim: Dimensionality of the embedding space
        """
        self.embedding_dim = embedding_dim
        self.context_field = ContextField(embedding_dim)
        self.initialized = False
    
    def initialize(self):
        """Initialize the recommendation engine components."""
        # Initialize context model and other components
        self.initialized = True
    
    def recommend(self, user_state: UserState, context: ContextSignals, 
                 items: List[Item], session_minutes: int = 60, 
                 slate_size: int = 6, spotify_data: Optional[dict] = None) -> Tuple[List[Item], Dict[str, Any]]:
        """
        Generate recommendations based on user state and context.
        
        Args:
            user_state: Current state of the user
            context: Current context/environment
            items: List of candidate items
            session_minutes: Expected session duration in minutes
            slate_size: Number of items to recommend
            spotify_data: Optional Spotify API data for context
            
        Returns:
            Tuple of (recommended items, UI metadata)
        """
        if not self.initialized:
            raise RuntimeError("Engine not initialized. Call initialize() first.")
        
        # Mise à jour du contexte avec les données Spotify si disponibles
        if spotify_data:
            context_manager = ContextManager()
            context_manager.update_from_spotify(spotify_data)
            context = context_manager.current_context
            
        # Log du contexte actuel pour le débogage
        context_summary = context_manager.get_context_summary() if 'context_manager' in locals() else {}
        logging.info(f"Context for recommendation: {context_summary}")
            
        return step_recommend(
            context_model=self.context_field,
            user=user_state,
            items=items,
            context=context,
            session_minutes=session_minutes,
            slate_size=slate_size
        )
    
    def update_user_state(self, user_state: UserState, 
                         watched: List[Tuple[str, float, bool]],
                         items_by_id: Dict[str, Item]) -> None:
        """
        Update user state based on interaction feedback.
        
        Args:
            user_state: The user state to update
            watched: List of (item_id, watch_ratio, liked_bool)
            items_by_id: Dictionary mapping item IDs to Item objects
        """
        online_update_after_interactions(
            user=user_state,
            watched=watched,
            items_by_id=items_by_id
        )

# ---------- Context Field (GRU stub) ----------

class ContextField:
    """Manages the context encoding and state transitions."""
    
    def __init__(self, d: int):
        """
        Initialize the context field.
        
        Args:
            d: Dimensionality of the context vector
        """
        self.d = d
        self.z0 = np.zeros(d)

    def encode_signals(self, x: ContextSignals) -> np.ndarray:
        """Encode context signals into a feature vector."""
        v = np.zeros(self.d)
        v[0] = x.hour / 24
        v[1] = ["soleil", "pluie", "nuage"].index(x.weather) / 3 if x.weather in ["soleil", "pluie", "nuage"] else 0.5
        v[2] = 1.0 if x.with_friends else 0.0
        # Add more features as needed
        return v

    def step(self, z_prev: np.ndarray, x: ContextSignals) -> np.ndarray:
        """
        Update the context state based on previous state and new signals.
        
        Args:
            z_prev: Previous context state
            x: New context signals
            
        Returns:
            Updated context state
        """
        d = self.d
        Wx = np.eye(d) * 0.5  # Fixed weights for MVP
        Wz = np.eye(d) * 0.8
        b = np.zeros(d)
        xvec = self.encode_signals(x)
        return np.tanh(Wz @ z_prev + Wx @ xvec + b)

# ---------- Taste Manifold Update ----------

def update_taste(g: np.ndarray, pos_embeds: List[np.ndarray], 
                neg_embeds: List[np.ndarray], eta: float = 0.05) -> np.ndarray:
    """
    Update the user's taste vector based on positive and negative feedback.
    
    Args:
        g: Current taste vector
        pos_embeds: List of positive item embeddings
        neg_embeds: List of negative item embeddings
        eta: Learning rate
        
    Returns:
        Updated taste vector
    """
    if pos_embeds:
        g = g + eta * np.mean(np.stack(pos_embeds), axis=0)
    if neg_embeds:
        g = g - eta * np.mean(np.stack(neg_embeds), axis=0)
    g = g / (np.linalg.norm(g) + 1e-8)
    return g

# ---------- Rhythm Compatibility ----------

def rhythm_compat(item_facet: int, last_facet: int, R: np.ndarray) -> float:
    """
    Calculate rhythm compatibility between the last and candidate facet.
    
    Args:
        item_facet: Candidate facet index
        last_facet: Last facet index
        R: Rhythm transition matrix
        
    Returns:
        Compatibility score
    """
    p = R[last_facet, item_facet]
    return float(p)

# ---------- Accounts Dynamics ----------

def decay_accounts(C: float, N: float, lamC: float = 0.97, 
                  lamN: float = 0.97) -> Tuple[float, float]:
    """
    Apply decay to comfort and novelty accounts.
    
    Args:
        C: Current comfort account value
        N: Current novelty account value
        lamC: Comfort decay rate
        lamN: Novelty decay rate
        
    Returns:
        Tuple of (updated_comfort, updated_novelty)
    """
    return max(0.0, C * lamC), max(0.0, N * lamN)

def novelty_boost(is_novel: bool, N: float, base: float = 0.5) -> float:
    """Calculate novelty boost based on novelty account."""
    return base * (1 + N) if is_novel else 0.0

def exposure_penalty(item_id: str, exposure: Dict[str, float], 
                   base: float = 1.0) -> float:
    """Calculate exposure penalty for an item."""
    return base * exposure.get(item_id, 0.0)

# ---------- Resonance Score ----------

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    return float(a.dot(b) / (na * nb))

def resonance(item: Item, user: UserState, alpha: float = 3.0, 
             beta: float = 2.0, eta: float = 1.5, gamma: float = 1.0, 
             delta: float = 1.0) -> float:
    """
    Calculate the resonance score for an item given user state.
    
    Args:
        item: The item to score
        user: Current user state
        alpha: Weight for taste alignment
        beta: Weight for context alignment
        eta: Weight for rhythm compatibility
        gamma: Weight for novelty boost
        delta: Weight for exposure penalty
        
    Returns:
        Resonance score
    """
    align_g = alpha * cosine(item.embedding, user.g)
    align_z = beta * cosine(item.embedding, user.z)
    r_comp = eta * rhythm_compat(facet_index(*item.facet), user.last_facet, user.R)
    is_novel = (user.exposure.get(item.id, 0.0) < 0.1)
    nov = gamma * novelty_boost(is_novel, user.N)
    fat = delta * exposure_penalty(item.id, user.exposure)
    return align_g + align_z + r_comp + nov - fat

# ---------- Target Distribution & Costs ----------

def target_distribution(user: UserState, session_minutes: int) -> Dict[int, float]:
    """
    Generate target distribution over facets.
    
    Args:
        user: Current user state
        session_minutes: Expected session duration
        
    Returns:
        Dictionary mapping facet indices to target probabilities
    """
    mass = np.ones(K)
    # Simple heuristic - can be replaced with learned policy
    fmt_pref = np.array([0.5, 1.0, 0.3])  # court, moyen, long
    mood_pref = np.array([0.7, 0.9, 0.6, 0.8])  # cosy, inspirant, énergique, contemplatif
    grid = np.outer(fmt_pref, mood_pref).reshape(-1)
    mass *= grid
    mass = mass * (1.0 + 0.2 * user.N)  # Encourage exploration when N is high
    mass = mass / mass.sum()
    return {k: mass[k] for k in range(K)}

def redundancy_penalty(chosen_embeds: List[np.ndarray], 
                      candidate: np.ndarray) -> float:
    """
    Calculate redundancy penalty for a candidate item.
    
    Args:
        chosen_embeds: List of embeddings of already chosen items
        candidate: Embedding of the candidate item
        
    Returns:
        Redundancy penalty score
    """
    if not chosen_embeds: 
        return 0.0
    sims = [cosine(e, candidate) for e in chosen_embeds]
    return float(max(0.0, np.mean(sims) - 0.6))  # Penalize if too similar to average chosen

def drop_risk(item: Item, user: UserState) -> float:
    """
    Estimate the risk of the user dropping the item.
    
    Args:
        item: The item to evaluate
        user: Current user state
        
    Returns:
        Drop risk score (higher is riskier)
    """
    risk = 0.0
    if item.duration_min > 120: 
        risk += 0.2
    return risk

def item_cost(item: Item, user: UserState, chosen_embeds: List[np.ndarray], 
             lamb: float = 0.5, xi: float = 0.5) -> float:
    """
    Calculate the total cost of including an item in the slate.
    
    Args:
        item: The item to evaluate
        user: Current user state
        chosen_embeds: List of embeddings of already chosen items
        lamb: Weight for redundancy penalty
        xi: Weight for drop risk
        
    Returns:
        Total cost score (lower is better)
    """
    res = resonance(item, user)
    red = redundancy_penalty(chosen_embeds, item.embedding)
    dr = drop_risk(item, user)
    return -res + lamb * red + xi * dr

# ---------- Entropic OT for Slate Selection ----------

def sinkhorn_plan(cost_mat: np.ndarray, mu: np.ndarray, 
                 reg: float = 0.5, iters: int = 100) -> np.ndarray:
    """
    Compute the Sinkhorn plan for optimal transport.
    
    Args:
        cost_mat: [F facets x I items] costs to assign items to facets
        mu: Target facet mass (sum=1)
        reg: Regularization parameter
        iters: Number of iterations
        
    Returns:
        Transport plan matrix
    """
    K, I = cost_mat.shape
    K_mu = mu.reshape(K, 1)
    K_mu = K_mu / (K_mu.sum() + 1e-8)

    K_matrix = np.exp(-cost_mat / max(1e-5, reg))  # Gibbs kernel
    u = np.ones((K, 1)) / K
    v = np.ones((1, I)) / I
    
    for _ in range(iters):
        u = K_mu / (K_matrix @ v.T + 1e-8)
        v = (1.0 / I) / (u.T @ K_matrix + 1e-8)  # Uniform item capacity proxy
        
    plan = np.diagflat(u.flatten()) @ K_matrix @ np.diagflat(v.flatten())
    return plan

def select_slate_by_ot(items: List[Item], user: UserState, 
                      session_minutes: int, slate_size: int = 6) -> List[Item]:
    """
    Select a slate of items using optimal transport.
    
    Args:
        items: List of candidate items
        user: Current user state
        session_minutes: Expected session duration
        slate_size: Number of items to select
        
    Returns:
        List of selected items
    """
    # Build facet targets
    td = target_distribution(user, session_minutes)
    facets = sorted(td.keys())
    mu = np.array([td[f] for f in facets])  # K-length
    
    # Build cost matrix
    I = len(items)
    cost = np.zeros((K, I))
    chosen_embeds = []  # Track embeddings of chosen items
    
    for f in facets:
        # Temporarily set user.last_facet to f for rhythm-compat in scoring
        saved = user.last_facet
        user.last_facet = f
        for j, it in enumerate(items):
            cost[f, j] = item_cost(it, user, chosen_embeds)
        user.last_facet = saved

    plan = sinkhorn_plan(cost, mu, reg=0.6, iters=80)
    
    # Soft assignment → get per-item total mass
    per_item_mass = plan.sum(axis=0)  # length I
    
    # Greedy pick with attention/duration constraint
    order = np.argsort(-per_item_mass)
    slate, total_min = [], 0
    
    for idx in order:
        if len(slate) >= slate_size: 
            break
            
        cand = items[idx]
        
        # Attention budget: keep within ~session_minutes*1.5 for flexibility
        if total_min + cand.duration_min <= session_minutes * 1.5:
            # Avoid redundancy
            if redundancy_penalty([s.embedding for s in slate], cand.embedding) < 0.15:
                slate.append(cand)
                total_min += cand.duration_min
                
    return slate

# ---------- UI Policy ----------

def ui_policy(context: ContextSignals, slate: List[Item], 
             user: UserState) -> Dict:
    """
    Generate UI presentation metadata for the slate.
    
    Args:
        context: Current context
        slate: List of recommended items
        user: Current user state
        
    Returns:
        Dictionary with UI presentation data
    """
    # Determine UI theme based on context
    bg = "dark" if context.weather in ("pluie", "nuage") or context.hour >= 20 else "light"
    tone = "cozy" if bg == "dark" else "bright"
    
    pitch = ("Pluie dehors, confort dedans. Voici tes pépites cosy."
             if bg == "dark" else
             "Matin lumineux ? Découvre, apprends, voyage.")
    
    # Generate card data for each item
    cards = []
    for it in slate:
        why_terms = []
        
        # Build rationale from resonance components
        if cosine(it.embedding, user.g) > 0.6: 
            why_terms.append("tes genres favoris")
        if cosine(it.embedding, user.z) > 0.6: 
            why_terms.append("adapté à ton moment")
        if it.duration_min <= 45 and context.hour >= 22: 
            why_terms.append("format court pour tard le soir")
        if it.duration_min <= 45 and context.hour < 12:  
            why_terms.append("format parfait pour le matin")
            
        why = "Parce qu'il correspond à " + ", ".join(why_terms) + "." if why_terms else "Découvre cette suggestion !"
        
        cards.append({
            "id": it.id,
            "title": it.title,
            "meta": f"{it.type} • {', '.join(it.genres[:2])} • {int(it.duration_min)} min",
            "why": why
        })
    
    return {
        "bg": bg, 
        "tone": tone, 
        "pitch": pitch, 
        "cards": cards
    }

# ---------- Core Step Function ----------

def step_recommend(context_model: ContextField,
                  user: UserState,
                  items: List[Item],
                  context: ContextSignals,
                  session_minutes: int = 60,
                  slate_size: int = 6) -> Tuple[List[Item], Dict]:
    """
    Generate recommendations for a single step.
    
    Args:
        context_model: The context model
        user: Current user state
        items: List of candidate items
        context: Current context
        session_minutes: Expected session duration
        slate_size: Number of items to recommend
        
    Returns:
        Tuple of (recommended items, UI metadata)
    """
    # Update context state
    user.z = context_model.step(user.z, context)

    # Decay accounts
    user.C, user.N = decay_accounts(user.C, user.N)

    # Build slate with OT
    slate = select_slate_by_ot(items, user, session_minutes, slate_size)

    # Generate UI layout
    ui = ui_policy(context, slate, user)
    
    return slate, ui

# ---------- Online Updates ----------

def online_update_after_interactions(user: UserState,
                                     watched: List[Tuple[str, float, bool]],
                                     items_by_id: Dict[str, Item]) -> None:
    """
    Update user state based on interaction feedback.
    
    Args:
        user: The user state to update
        watched: List of tuples (item_id, watch_ratio, liked_bool)
        items_by_id: Dictionary mapping item IDs to Item objects
    """
    for iid, ratio, liked in watched:
        it = items_by_id.get(iid)
        if it:
            facet_idx = facet_index(*it.facet)
            user.update_after_interaction(
                item_id=iid,
                item_embedding=it.embedding,
                facet_idx=facet_idx,
                watch_ratio=ratio,
                liked=liked
            )

