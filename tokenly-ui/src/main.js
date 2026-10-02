import './style.css';

const tokens = [
  { symbol: 'BTC', name: 'Bitcoin', price: '$67,842.20', change: 4.82, marketCap: '$1.34T', volume: '$38.2B', score: 86, signal: 'Strong', status: 'positive', tags: ['#ETFflow', '#StoreOfValue'], spark: [32, 35, 33, 38, 36, 44, 47, 46, 53, 58, 56, 64], indicators: { rsi: 64, macd: 'Bullish', trend: 'Above 20D', volume: '+18.4%' }, context: 'Momentum is broadening after a clean reclaim of the 20-day trend line. ETF inflows are keeping the bid healthy.' },
  { symbol: 'ETH', name: 'Ethereum', price: '$3,548.61', change: 2.16, marketCap: '$426.7B', volume: '$18.7B', score: 79, signal: 'Healthy', status: 'positive', tags: ['#Restaking', '#L2Season'], spark: [44, 42, 46, 45, 49, 48, 55, 52, 56, 54, 60, 62], indicators: { rsi: 58, macd: 'Bullish', trend: 'Above 50D', volume: '+9.7%' }, context: 'Relative strength is improving as L2 activity re-accelerates. Watch for a decisive break above the local range.' },
  { symbol: 'SOL', name: 'Solana', price: '$184.93', change: 8.71, marketCap: '$85.9B', volume: '$6.4B', score: 91, signal: 'Leading', status: 'positive', tags: ['#MemeSummer', '#DePIN'], spark: [30, 33, 31, 40, 37, 46, 51, 49, 58, 62, 68, 75], indicators: { rsi: 72, macd: 'Strong bull', trend: 'Above 20D', volume: '+41.2%' }, context: 'SOL is the clearest momentum leader in this screen. Social velocity and volume expansion are confirming the move.' },
  { symbol: 'LINK', name: 'Chainlink', price: '$16.42', change: -1.38, marketCap: '$10.2B', volume: '$792M', score: 63, signal: 'Neutral', status: 'neutral', tags: ['#RWA', '#Oracle'], spark: [57, 54, 56, 53, 51, 54, 52, 49, 51, 50, 48, 46], indicators: { rsi: 46, macd: 'Flat', trend: 'At 50D', volume: '-4.1%' }, context: 'The setup is constructive but waiting for a catalyst. Volume has cooled while price compresses near the 50-day average.' },
  { symbol: 'AVAX', name: 'Avalanche', price: '$38.24', change: -3.29, marketCap: '$15.1B', volume: '$402M', score: 48, signal: 'Cooling', status: 'negative', tags: ['#Subnets', '#Gaming'], spark: [62, 61, 58, 60, 55, 52, 54, 49, 50, 47, 44, 41], indicators: { rsi: 38, macd: 'Bearish', trend: 'Below 20D', volume: '-16.8%' }, context: 'Price is losing trend support and attention is fading. A recovery above the 20-day line would be the first repair signal.' },
  { symbol: 'ARB', name: 'Arbitrum', price: '$0.894', change: 5.43, marketCap: '$3.2B', volume: '$287M', score: 74, signal: 'Building', status: 'positive', tags: ['#L2Season', '#Airdrop'], spark: [38, 36, 39, 42, 40, 43, 47, 45, 49, 54, 52, 59], indicators: { rsi: 61, macd: 'Bullish', trend: 'Above 20D', volume: '+23.1%' }, context: 'ARB is showing early participation from both price and social attention. Follow-through above resistance would improve conviction.' },
  { symbol: 'DOGE', name: 'Dogecoin', price: '$0.168', change: 3.92, marketCap: '$24.3B', volume: '$1.1B', score: 68, signal: 'Warming', status: 'positive', tags: ['#MemeSummer', '#Retail'], spark: [42, 40, 44, 43, 49, 46, 52, 55, 53, 59, 61, 64], indicators: { rsi: 59, macd: 'Bullish', trend: 'Above 50D', volume: '+15.6%' }, context: 'Attention is returning with meme-coin discussion accelerating. Confirmation still depends on sustained volume above the local range.' },
  { symbol: 'RNDR', name: 'Render', price: '$9.12', change: 6.18, marketCap: '$4.7B', volume: '$318M', score: 76, signal: 'Building', status: 'positive', tags: ['#DePIN', '#AI'], spark: [37, 39, 38, 43, 42, 47, 46, 51, 55, 54, 59, 66], indicators: { rsi: 63, macd: 'Bullish', trend: 'Above 20D', volume: '+28.4%' }, context: 'AI compute and DePIN chatter are reinforcing a constructive setup. A clean break of resistance would increase the signal score.' },
];

const trends = [
  { topic: '#ETFflow', category: 'Macro', momentum: 92, delta: '+18%', mentions: '184K', velocity: 'Exploding', color: 'coral', tokens: ['BTC', 'ETH'], note: 'Spot ETF inflow chatter is back at the center of crypto timelines.' },
  { topic: '#MemeSummer', category: 'Culture', momentum: 84, delta: '+31%', mentions: '139K', velocity: 'Accelerating', color: 'lavender', tokens: ['SOL', 'DOGE'], note: 'Creator-led meme launches are driving a new wave of retail attention.' },
  { topic: '#L2Season', category: 'Ecosystem', momentum: 78, delta: '+12%', mentions: '96K', velocity: 'Rising', color: 'mint', tokens: ['ETH', 'ARB'], note: 'Scaling narratives are warming up as activity shifts toward app-specific chains.' },
  { topic: '#DePIN', category: 'Infrastructure', momentum: 69, delta: '+9%', mentions: '72K', velocity: 'Rising', color: 'amber', tokens: ['SOL', 'RNDR'], note: 'Physical infrastructure and AI compute remain a durable crossover narrative.' },
];

const state = { view: 'overview', search: '', timeframe: '24H', sort: 'score', filter: 'all', selected: 'SOL', selectedTrend: 0, toast: '' };

const icon = (name, size = 20) => {
  const paths = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    radar: '<circle cx="12" cy="12" r="8"/><path d="m12 12 6-6M12 4v2M4 12h2M12 18v2M18 12h2"/><circle cx="12" cy="12" r="2"/>',
    flame: '<path d="M12.5 21c4.3-.3 7.2-3 7.2-7.1 0-3.4-2-6.3-5.2-8.9.1 2-1.1 3.4-2.4 4.3.2-3.2-1.1-6-3.8-8.3.3 4-3.8 6.4-3.8 11 0 4.7 3.3 8.8 8 9Z"/><path d="M12 21c-2.2-.4-3.8-2-3.8-4.2 0-1.5.8-2.9 2.2-4.1.1 1.4.7 2.4 1.8 3.1.3-1.2 1-2.1 2-2.8.3 1.2 1.6 2.7 1.6 4.4 0 1.8-1.3 3.3-3.8 3.6Z"/>',
    bookmark: '<path d="M6 4.8A2.8 2.8 0 0 1 8.8 2h6.4A2.8 2.8 0 0 1 18 4.8V22l-6-3.7L6 22V4.8Z"/>',
    settings: '<path d="M12 15.2a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4Z"/><path d="m19.4 15 .1.1a2 2 0 0 1-2.8 2.8l-.1-.1a2 2 0 0 0-3.4 1.4v.2a2 2 0 1 1-4 0v-.2a2 2 0 0 0-3.4-1.4l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A2 2 0 0 0 4.4 12a2 2 0 0 0-1.4-3.4h-.2a2 2 0 1 1 0-4H3a2 2 0 0 0 1.4-3.4l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A2 2 0 0 0 10.6 4a2 2 0 0 0 1.4-3.4h.2a2 2 0 1 1 0 4h-.2A2 2 0 0 0 13.4 8a2 2 0 0 0 3.4-1.4v-.2a2 2 0 1 1 4 0v.2A2 2 0 0 0 22.2 8h.2a2 2 0 1 1 0 4h-.2A2 2 0 0 0 19.4 15Z" transform="translate(-1 -1) scale(.95)"/>',
    search: '<circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/>',
    bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4"/>',
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    chevron: '<path d="m9 18 6-6-6-6"/>',
    up: '<path d="m5 15 5-5 3 3 6-7"/><path d="M19 6h-5M19 6v5"/>',
    sliders: '<path d="M4 6h10M18 6h2M4 12h2M10 12h10M4 18h10M18 18h2"/><circle cx="16" cy="6" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="16" cy="18" r="2"/>',
    clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
    external: '<path d="M14 5h5v5M19 5l-8 8"/><path d="M18 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  };
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.grid}</svg>`;
};

const sparkline = (values, color = '#ff6b5f') => {
  const min = Math.min(...values), max = Math.max(...values);
  const points = values.map((v, i) => `${(i / (values.length - 1)) * 100},${34 - ((v - min) / (max - min || 1)) * 26}`).join(' ');
  return `<svg class="sparkline" viewBox="0 0 100 40" preserveAspectRatio="none" aria-label="Price momentum sparkline"><polyline points="${points}" fill="none" stroke="${color}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
};

const avatar = (symbol, color) => `<div class="token-avatar ${color || ''}">${symbol.slice(0, 1)}</div>`;
const selectedToken = () => tokens.find((token) => token.symbol === state.selected) || tokens[0];
const filteredTokens = () => tokens.filter((token) => `${token.symbol} ${token.name} ${token.tags.join(' ')}`.toLowerCase().includes(state.search.toLowerCase())).filter((token) => state.filter === 'all' || token.score >= 70).sort((a, b) => state.sort === 'change' ? b.change - a.change : state.sort === 'marketCap' ? parseFloat(b.marketCap) - parseFloat(a.marketCap) : b.score - a.score);

function navItem(view, label, iconName) {
  return `<button class="nav-item ${state.view === view ? 'active' : ''}" data-view="${view}"><span class="nav-icon">${icon(iconName, 18)}</span><span>${label}</span>${view === 'trends' ? '<span class="nav-count">4</span>' : ''}</button>`;
}

function appShell(content) {
  return `<div class="app-shell">
    <aside class="sidebar">
      <div class="brand"><div class="brand-mark"><span></span><span></span></div><span>tokenly</span></div>
      <div class="workspace-chip"><span class="pulse-dot"></span><span>Market pulse</span><span class="chip-caret">⌄</span></div>
      <div class="nav-label">Workspace</div>
      <nav class="main-nav">${navItem('overview', 'Overview', 'grid')}${navItem('screener', 'Screener', 'radar')}${navItem('trends', 'Social trends', 'flame')}${navItem('watchlist', 'Watchlist', 'bookmark')}</nav>
      <div class="nav-label nav-label-bottom">Personalize</div>
      <nav class="main-nav">${navItem('settings', 'Settings', 'settings')}</nav>
      <div class="sidebar-bottom"><div class="pro-card"><div class="pro-card-title">Stay ahead<br/>of the chatter.</div><p>Unlock more signal layers and saved screens.</p><button class="mini-button" data-action="upgrade">Explore pro <span>↗</span></button></div><div class="user-row"><div class="user-avatar">JD</div><div><strong>Jordan Davis</strong><span>Researcher</span></div><button class="more-button">•••</button></div></div>
    </aside>
    <main class="main-content"><header class="topbar"><div class="mobile-brand"><div class="brand-mark"><span></span><span></span></div><span>tokenly</span></div><div class="breadcrumb"><span>Workspace</span><span class="breadcrumb-slash">/</span><strong>${state.view === 'trends' ? 'Social trends' : state.view === 'screener' ? 'Screener' : 'Overview'}</strong></div><div class="topbar-actions"><div class="search-box">${icon('search', 17)}<input id="global-search" value="${state.search}" placeholder="Search tokens" aria-label="Search tokens"/></div><button class="icon-button has-notification" aria-label="Notifications">${icon('bell', 19)}<i></i></button><button class="top-avatar">JD</button></div></header>${content}</main>
    <nav class="mobile-nav">${navItem('overview', 'Home', 'grid')}${navItem('screener', 'Scan', 'radar')}${navItem('trends', 'Trends', 'flame')}${navItem('watchlist', 'Saved', 'bookmark')}</nav>
  </div>`;
}

function pageHeader(eyebrow, title, description, action) {
  return `<div class="page-header"><div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1><p>${description}</p></div>${action || ''}</div>`;
}

function marketStrip() {
  return `<div class="market-strip"><div class="strip-label"><span class="pulse-dot"></span><span>Live market</span></div><div class="market-item"><span>BTC dominance</span><strong>52.8%</strong><b class="positive-text">+0.4%</b></div><div class="market-item"><span>Fear & greed</span><strong>72 <small>Greed</small></strong></div><div class="market-item"><span>Total market cap</span><strong>$2.54T</strong><b class="positive-text">+2.8%</b></div><div class="market-item"><span>24h volume</span><strong>$88.6B</strong></div><div class="strip-time">Updated 2m ago ${icon('clock', 13)}</div></div>`;
}

function metricCard(label, value, delta, iconName, tone, sub) {
  return `<div class="metric-card clay-card"><div class="metric-top"><span>${label}</span><span class="metric-icon ${tone}">${icon(iconName, 16)}</span></div><div class="metric-value">${value}</div><div class="metric-footer"><span class="${tone === 'negative' ? 'negative-text' : 'positive-text'}">${delta}</span><span>${sub}</span></div></div>`;
}

function screenerControls() {
  return `<div class="screener-controls"><div class="control-tabs"><button class="control-tab active">${state.filter === 'all' ? 'All tokens' : 'High conviction'} <span>${filteredTokens().length}</span></button><button class="control-tab">My watchlist <span>8</span></button></div><div class="control-actions"><button class="soft-button" data-action="filter">${icon('sliders', 16)} Filters <span class="filter-badge">${state.filter === 'all' ? '3' : '1'}</span></button><div class="select-wrap"><select id="sort-select" aria-label="Sort tokens"><option value="score" ${state.sort === 'score' ? 'selected' : ''}>Sort: Signal score</option><option value="change" ${state.sort === 'change' ? 'selected' : ''}>Sort: 24h change</option><option value="marketCap" ${state.sort === 'marketCap' ? 'selected' : ''}>Sort: Market cap</option></select></div></div></div>`;
}

function tokenRow(token) {
  const avatarTone = token.symbol === 'SOL' ? 'orange' : token.symbol === 'ETH' ? 'purple' : token.symbol === 'LINK' ? 'blue' : token.symbol === 'AVAX' ? 'red' : 'gold';
  return `<button class="token-row ${state.selected === token.symbol ? 'selected' : ''}" data-token="${token.symbol}"><div class="token-identity">${avatar(token.symbol, avatarTone)}<div><strong>${token.symbol}</strong><span>${token.name}</span></div></div><div class="token-price"><strong>${token.price}</strong><span class="${token.change >= 0 ? 'positive-text' : 'negative-text'}">${token.change >= 0 ? '+' : ''}${token.change.toFixed(2)}%</span></div><div class="token-chart">${sparkline(token.spark, token.change >= 0 ? '#3bb891' : '#ed7c73')}</div><div class="token-indicator"><span class="status-bead ${token.status}"></span><span>${token.signal}</span></div><div class="score-pill ${token.status}">${token.score}<small>/100</small></div><span class="row-chevron">${icon('chevron', 17)}</span></button>`;
}

function screenerTable() {
  const rows = filteredTokens().map(tokenRow).join('');
  return `<div class="screener-table clay-card"><div class="table-head"><span>Asset</span><span>Price / 24h</span><span>Trend</span><span>Signal</span><span>Score</span><span></span></div><div class="table-body">${rows || '<div class="empty-state"><div class="empty-icon">⌕</div><strong>No tokens match that search.</strong><p>Try another symbol or topic tag.</p></div>'}</div><div class="table-footer"><span>Showing ${filteredTokens().length} of 248 screened assets</span><button class="text-button" data-action="view-all">View full screener ${icon('arrow', 15)}</button></div></div>`;
}

function detailRail() {
  const token = selectedToken();
  const tones = { BTC: 'gold', ETH: 'purple', SOL: 'orange', LINK: 'blue', AVAX: 'red', ARB: 'blue' };
  return `<aside class="detail-rail clay-card"><div class="detail-heading"><div><div class="eyebrow">Selected asset</div><div class="detail-title-row">${avatar(token.symbol, tones[token.symbol])}<div><h2>${token.name}</h2><span>${token.symbol} · Spot market</span></div></div></div><button class="close-detail" aria-label="Close detail">×</button></div><div class="detail-price"><strong>${token.price}</strong><span class="${token.change >= 0 ? 'positive-text' : 'negative-text'}">${token.change >= 0 ? '+' : ''}${token.change.toFixed(2)}%</span></div><div class="detail-chart">${sparkline(token.spark, token.change >= 0 ? '#ff6b5f' : '#ed7c73')}<div class="chart-labels"><span>09:00</span><span>Now</span></div></div><div class="detail-section"><div class="section-kicker">Signal breakdown <span>Live</span></div><div class="signal-score-row"><span class="large-score">${token.score}</span><div><strong>${token.signal} signal</strong><p>Strongest read across your current screen.</p></div><div class="score-ring" style="--score:${token.score * 3.6}deg"><span>${token.score}</span></div></div><div class="indicator-list"><div><span>RSI (14)</span><strong>${token.indicators.rsi}</strong><em class="${token.indicators.rsi > 70 ? 'amber-text' : 'positive-text'}">${token.indicators.rsi > 70 ? 'Hot' : 'Healthy'}</em></div><div><span>MACD</span><strong>${token.indicators.macd}</strong><em class="positive-text">Confirmed</em></div><div><span>Trend</span><strong>${token.indicators.trend}</strong><em class="positive-text">Aligned</em></div><div><span>Volume</span><strong>${token.indicators.volume}</strong><em class="${token.indicators.volume.startsWith('-') ? 'negative-text' : 'positive-text'}">${token.indicators.volume.startsWith('-') ? 'Fading' : 'Expanding'}</em></div></div></div><div class="detail-section context-section"><div class="section-kicker">Market context</div><p>${token.context}</p><div class="tag-row">${token.tags.map((tag) => `<span class="tag">${tag}</span>`).join('')}</div></div><button class="primary-button full-button" data-action="add-watchlist">${icon('bookmark', 16)} Add to watchlist</button></aside>`;
}

function overviewView() {
  return `${pageHeader('Monday, April 22 · 09:41 UTC', 'Find the signal before the crowd.', 'Scan market structure, technical health, and social energy in one calm workspace.', '<button class="primary-button" data-action="new-screen">+ New screen</button>')}${marketStrip()}<div class="metric-grid">${metricCard('Screened assets', '248', '+12', 'radar', 'coral', 'since yesterday')}${metricCard('Strong signals', '34', '+8.4%', 'up', 'mint', 'vs. last scan')}${metricCard('Trending topics', '17', '+5', 'flame', 'lavender', 'in the last 24h')}${metricCard('Watchlist pulse', '68/100', '+4.2', 'bookmark', 'amber', 'signal strength')}</div><section class="section-block"><div class="section-heading"><div><div class="eyebrow">Market radar</div><h2>What deserves a closer look?</h2></div><div class="timeframe-tabs">${['1H', '24H', '7D'].map((time) => `<button class="time-tab ${state.timeframe === time ? 'active' : ''}" data-timeframe="${time}">${time}</button>`).join('')}</div></div><div class="dashboard-grid"><div class="screener-panel">${screenerControls()}${screenerTable()}</div>${detailRail()}</div></section><section class="section-block trend-block"><div class="section-heading"><div><div class="eyebrow">Social pulse</div><h2>Where the conversation is moving</h2></div><button class="text-button" data-view="trends">See all trends ${icon('arrow', 15)}</button></div><div class="trend-preview-grid">${trends.slice(0, 3).map((trend, index) => trendCard(trend, index)).join('')}</div></section>`;
}

function trendCard(trend, index) {
  return `<button class="trend-card clay-card ${state.selectedTrend === index ? 'selected' : ''}" data-trend="${index}"><div class="trend-card-top"><span class="topic-dot ${trend.color}"></span><span class="trend-category">${trend.category}</span><span class="trend-time">2h</span></div><div class="trend-topic">${trend.topic}</div><div class="trend-metrics"><strong>${trend.momentum}</strong><span>momentum</span><b class="positive-text">${trend.delta}</b></div><div class="momentum-bar"><i style="width:${trend.momentum}%"></i></div><div class="related-row"><span>Related</span>${trend.tokens.map((token) => `<b>${token}</b>`).join('')}<span class="related-arrow">${icon('arrow', 14)}</span></div></button>`;
}

function screenerView() {
  return `${pageHeader('Signal lab', 'Screen the market your way.', 'Stack simple criteria, then compare signal strength across the assets that pass.', '<button class="soft-button" data-action="save-screen">${icon("bookmark", 16)} Save screen</button>')}${marketStrip()}<section class="section-block screener-page"><div class="screen-builder clay-card"><div><div class="eyebrow">Active screen</div><h2>Momentum with confirmation</h2><p>Showing tokens with a healthy trend, expanding volume, and a positive social pulse.</p></div><div class="builder-chips"><span class="builder-chip">RSI <b>40–72</b> ×</span><span class="builder-chip">MACD <b>Bullish</b> ×</span><span class="builder-chip">Volume <b>Expanding</b> ×</span><button class="add-filter">+ Add filter</button></div></div><div class="dashboard-grid"><div class="screener-panel">${screenerControls()}${screenerTable()}</div>${detailRail()}</div></section>`;
}

function trendsView() {
  const selected = trends[state.selectedTrend];
  return `${pageHeader('Social listening', 'Trace the chatter to the chart.', 'Track what crypto communities are discussing, then see which tokens are riding the same narrative.', '<button class="primary-button" data-action="refresh-trends">${icon("radar", 16)} Refresh pulse</button>')}${marketStrip()}<section class="section-block trends-page"><div class="trend-layout"><div class="trend-list-panel clay-card"><div class="panel-heading"><div><div class="eyebrow">Live topics</div><h2>Trending now</h2></div><span class="live-label"><i></i> Streaming</span></div><div class="trend-list">${trends.map((trend, index) => `<button class="trend-list-item ${state.selectedTrend === index ? 'selected' : ''}" data-trend="${index}"><span class="topic-dot ${trend.color}"></span><div class="trend-list-copy"><strong>${trend.topic}</strong><span>${trend.category} · ${trend.mentions} mentions</span></div><div class="trend-list-score"><b>${trend.momentum}</b><span class="positive-text">${trend.delta}</span></div><span>${icon('chevron', 16)}</span></button>`).join('')}</div><div class="trend-footnote">Topic signals combine velocity, engagement quality, and 24h mention volume.</div></div><div class="trend-detail clay-card"><div class="trend-detail-top"><div><div class="eyebrow">Narrative map</div><h2>${selected.topic}</h2><p>${selected.note}</p></div><span class="big-momentum">${selected.momentum}<small>momentum</small></span></div><div class="relationship-map"><div class="topic-node ${selected.color}"><span>Topic</span><strong>${selected.topic}</strong><small>${selected.mentions} mentions</small></div><div class="map-lines"><span></span><span></span></div><div class="token-nodes">${selected.tokens.map((symbol, index) => { const token = tokens.find(t => t.symbol === symbol); return `<button class="related-token" data-token="${symbol}">${avatar(symbol, index ? 'purple' : 'orange')}<span><strong>${symbol}</strong><small>${token ? token.name : 'Token'}</small></span><b>${token ? (token.change > 0 ? '+' : '') + token.change.toFixed(2) + '%' : '+3.8%'}</b></button>`; }).join('')}</div></div><div class="topic-breakdown"><div><span>Velocity</span><strong>${selected.velocity}</strong><em class="positive-text">${selected.delta}</em></div><div><span>Engagement quality</span><strong>High intent</strong><em>82/100</em></div><div><span>Top source</span><strong>Crypto Twitter</strong><em>${selected.mentions} posts</em></div></div><button class="primary-button full-button" data-action="follow-topic">${icon("bookmark", 16)} Follow topic</button></div></div></section>`;
}

function toast(message) { state.toast = message; render(); setTimeout(() => { state.toast = ''; render(); }, 2400); }
function render() {
  let content = state.view === 'trends' ? trendsView() : state.view === 'screener' ? screenerView() : overviewView();
  document.querySelector('#app').innerHTML = appShell(content) + (state.toast ? `<div class="toast">${icon('up', 16)} ${state.toast}</div>` : '');
  bindEvents();
}
function bindEvents() {
  document.querySelectorAll('[data-view]').forEach((el) => el.addEventListener('click', () => { state.view = el.dataset.view; if (state.view === 'watchlist' || state.view === 'settings') toast(`${state.view === 'watchlist' ? 'Watchlist' : 'Settings'} is coming next.`); else render(); }));
  document.querySelectorAll('[data-token]').forEach((el) => el.addEventListener('click', () => { state.selected = el.dataset.token; render(); }));
  document.querySelectorAll('[data-trend]').forEach((el) => el.addEventListener('click', () => { state.selectedTrend = Number(el.dataset.trend); if (state.view !== 'trends') state.view = 'trends'; render(); }));
  document.querySelectorAll('[data-timeframe]').forEach((el) => el.addEventListener('click', () => { state.timeframe = el.dataset.timeframe; render(); }));
  const search = document.querySelector('#global-search'); if (search) search.addEventListener('input', (e) => { state.search = e.target.value; render(); const input = document.querySelector('#global-search'); input.focus(); input.setSelectionRange(input.value.length, input.value.length); });
  const sort = document.querySelector('#sort-select'); if (sort) sort.addEventListener('change', (e) => { state.sort = e.target.value; render(); });
  document.querySelectorAll('[data-action]').forEach((el) => el.addEventListener('click', () => { const action = el.dataset.action; if (action === 'refresh-trends') toast('Social pulse refreshed · 2 minutes ago'); if (action === 'add-watchlist') toast(`${selectedToken().symbol} added to your watchlist`); if (action === 'follow-topic') toast(`${trends[state.selectedTrend].topic} is now followed`); if (action === 'save-screen') toast('Screen saved to your workspace'); if (action === 'new-screen') toast('New screen builder opened'); if (action === 'filter') { state.filter = state.filter === 'all' ? 'positive' : 'all'; render(); } if (action === 'upgrade') toast('Pro preview is coming soon'); if (action === 'view-all') { state.view = 'screener'; render(); } }));
}
render();
