(function () {
  'use strict'

  const $ = (s, r = document) => r.querySelector(s)
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s))
  const root = document.documentElement

  /* ---------- theme ---------- */

  const themeMeta = $('meta[name="theme-color"]')
  function applyTheme(theme) {
    root.dataset.theme = theme
    if (themeMeta) themeMeta.setAttribute('content', theme === 'dark' ? '#0f1115' : '#f6f3ee')
    try { localStorage.setItem('venus-theme', theme) } catch (e) {}
  }
  $$('.theme-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      applyTheme(root.dataset.theme === 'dark' ? 'light' : 'dark')
    })
  })

  /* ---------- header ---------- */

  const header = $('#siteHeader')
  const toTop = $('#toTop')
  let ticking = false
  function onScroll() {
    if (ticking) return
    ticking = true
    requestAnimationFrame(() => {
      const y = window.scrollY
      if (header && header.classList.contains('site-header--overlay')) {
        header.classList.toggle('is-scrolled', y > 24)
      }
      if (toTop) toTop.classList.toggle('is-visible', y > 720)
      updateReading(y)
      ticking = false
    })
  }

  /* ---------- drawer ---------- */

  const drawer = $('#drawer')
  const menuToggle = $('.menu-toggle')
  function setDrawer(open) {
    if (!drawer) return
    drawer.classList.toggle('is-open', open)
    drawer.setAttribute('aria-hidden', open ? 'false' : 'true')
    document.body.classList.toggle('is-locked', open)
    if (menuToggle) menuToggle.setAttribute('aria-expanded', String(open))
    if (open) {
      const first = drawer.querySelector('a, button')
      if (first) setTimeout(() => first.focus(), 60)
    } else if (menuToggle) {
      menuToggle.focus()
    }
  }
  if (menuToggle) {
    menuToggle.addEventListener('click', () => setDrawer(!drawer.classList.contains('is-open')))
  }
  $$('[data-drawer-close]').forEach(el => el.addEventListener('click', () => setDrawer(false)))

  /* ---------- search ---------- */

  const modal = $('#searchModal')
  const input = $('#searchInput')
  const resultsBox = $('#searchResults')
  let searchData = null
  let searchLoading = false
  let selected = -1
  let lastFocus = null

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
  }

  function openSearch() {
    if (!modal) return
    lastFocus = document.activeElement
    modal.hidden = false
    document.body.classList.add('is-locked')
    setTimeout(() => input && input.focus(), 40)
    if (searchData === null && !searchLoading) loadSearch()
    else if (searchData) renderSearch(input.value)
  }
  function closeSearch() {
    if (!modal || modal.hidden) return
    modal.hidden = true
    document.body.classList.remove('is-locked')
    selected = -1
    if (lastFocus) lastFocus.focus()
  }
  async function loadSearch() {
    searchLoading = true
    try {
      const res = await fetch('/search.json')
      if (!res.ok) throw new Error('bad status')
      searchData = await res.json()
      renderSearch(input.value)
    } catch (e) {
      searchData = []
      resultsBox.innerHTML = '<p class="search-empty">搜索数据加载失败，请稍后再试。</p>'
    }
    searchLoading = false
  }

  function scoreItem(item, q) {
    const title = item.title.toLowerCase()
    const tags = item.tags.join(' ').toLowerCase()
    const cats = item.categories.join(' ').toLowerCase()
    const excerpt = (item.excerpt || '').toLowerCase()
    const text = (item.text || '').toLowerCase()
    let score = 0
    if (title.includes(q)) score += 10
    if (tags.includes(q)) score += 6
    if (cats.includes(q)) score += 5
    if (excerpt.includes(q)) score += 3
    if (text.includes(q)) score += 1
    return score
  }

  function renderSearch(raw) {
    if (!resultsBox) return
    const q = (raw || '').trim().toLowerCase()
    if (!q) {
      resultsBox.innerHTML = '<p class="search-hint">输入关键词开始搜索，试试「python」或「生信」。</p>'
      selected = -1
      return
    }
    if (!searchData || !searchData.length) {
      resultsBox.innerHTML = '<p class="search-empty">还没有可搜索的文章。</p>'
      return
    }
    const hits = searchData
      .map(item => ({ item, score: scoreItem(item, q) }))
      .filter(x => x.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 8)

    if (!hits.length) {
      resultsBox.innerHTML = `<p class="search-empty">没有找到与「${escapeHtml(raw.trim())}」相关的文章。</p>`
      selected = -1
      return
    }

    resultsBox.innerHTML = hits.map(({ item }, i) => `
      <a class="search-result${i === 0 ? ' is-selected' : ''}" href="${escapeHtml(item.url)}" data-index="${i}">
        <img src="${escapeHtml(item.cover)}" alt="" loading="lazy">
        <span>
          <span class="search-result-title">${escapeHtml(item.title)}</span>
          <span class="search-result-meta"><span>${escapeHtml(item.categories.join(' · '))}</span>${item.date.replaceAll('-', '.')} · ${escapeHtml(item.tags.map(t => '#' + t).join(' '))}</span>
        </span>
      </a>`).join('') + `<div class="search-footnote"><span><kbd>↑</kbd><kbd>↓</kbd> 选择</span><span><kbd>Enter</kbd> 打开</span><span><kbd>Esc</kbd> 关闭</span></div>`
    selected = 0
  }

  function moveSelection(delta) {
    const items = $$('.search-result', resultsBox)
    if (!items.length) return
    selected = (selected + delta + items.length) % items.length
    items.forEach((el, i) => el.classList.toggle('is-selected', i === selected))
    const el = items[selected]
    if (el) el.scrollIntoView({ block: 'nearest' })
  }

  $$('.search-open').forEach(btn => btn.addEventListener('click', openSearch))
  $$('[data-search-close]').forEach(el => el.addEventListener('click', closeSearch))
  if (input) {
    input.addEventListener('input', e => renderSearch(e.target.value))
    input.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown') { e.preventDefault(); moveSelection(1) }
      else if (e.key === 'ArrowUp') { e.preventDefault(); moveSelection(-1) }
      else if (e.key === 'Enter') {
        const el = $$('.search-result', resultsBox)[selected]
        if (el) { window.location.href = el.getAttribute('href') }
      }
    })
  }
  if (resultsBox) {
    resultsBox.addEventListener('mousemove', e => {
      const card = e.target.closest('.search-result')
      if (!card) return
      const items = $$('.search-result', resultsBox)
      selected = items.indexOf(card)
      items.forEach((el, i) => el.classList.toggle('is-selected', i === selected))
    })
  }
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault()
      if (modal && modal.hidden) openSearch()
      else closeSearch()
      return
    }
    if (e.key === 'Escape') {
      if (modal && !modal.hidden) closeSearch()
      else if (drawer && drawer.classList.contains('is-open')) setDrawer(false)
    }
  })

  /* ---------- article list filter ---------- */

  const grid = $('#postGrid')
  if (grid) {
    const cards = $$('.post-card', grid)
    const chips = $$('.chip-btn', $('#articleToolbar'))
    const search = $('#articleSearch')
    const status = $('#listStatus')
    const empty = $('#emptyState')
    const params = new URLSearchParams(location.search)
    let activeCat = params.get('category') || 'all'
    let activeTag = params.get('tag') || ''
    let keyword = ''

    const known = chips.map(c => c.dataset.filter)
    if (!known.includes(activeCat)) activeCat = 'all'

    function apply() {
      let shown = 0
      cards.forEach(card => {
        const cats = (card.dataset.category || '').split('|')
        const tags = (card.dataset.tag || '').split('|')
        const text = (card.dataset.title + ' ' + card.dataset.text).toLowerCase()
        const okCat = activeCat === 'all' || cats.includes(activeCat)
        const okTag = !activeTag || tags.includes(activeTag)
        const okKw = !keyword || text.includes(keyword)
        const ok = okCat && okTag && okKw
        card.hidden = !ok
        if (ok) shown++
      })
      chips.forEach(c => c.classList.toggle('is-active', c.dataset.filter === activeCat))
      if (empty) empty.hidden = shown !== 0

      if (status) {
        const parts = []
        if (activeCat !== 'all') parts.push(`分类「${activeCat}」`)
        if (activeTag) parts.push(`标签「${activeTag}」`)
        if (keyword) parts.push(`关键词「${keyword}」`)
        status.innerHTML = parts.length
          ? `筛选：${parts.join(' + ')}，共 <strong>${shown}</strong> 篇 <button type="button" data-clear-filter>清除筛选</button>`
          : `共 <strong>${shown}</strong> 篇文章`
        const clear = $('[data-clear-filter]', status)
        if (clear) clear.addEventListener('click', () => {
          activeCat = 'all'; activeTag = ''; keyword = ''
          if (search) search.value = ''
          history.replaceState(null, '', location.pathname)
          apply()
        })
      }
    }

    chips.forEach(chip => chip.addEventListener('click', () => {
      activeCat = chip.dataset.filter
      activeTag = ''
      const url = new URL(location.href)
      if (activeCat === 'all') url.searchParams.delete('category')
      else url.searchParams.set('category', activeCat)
      url.searchParams.delete('tag')
      history.replaceState(null, '', url)
      apply()
    }))
    if (search) search.addEventListener('input', e => {
      keyword = e.target.value.trim().toLowerCase()
      apply()
    })
    apply()
  }

  /* ---------- reveal ---------- */

  const reveals = $$('[data-reveal]')
  if ('IntersectionObserver' in window && reveals.length && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const io = new IntersectionObserver(entries => {
      entries.forEach((entry, i) => {
        if (!entry.isIntersecting) return
        const el = entry.target
        el.style.animationDelay = Math.min(i * 60, 240) + 'ms'
        el.classList.add('is-revealed')
        io.unobserve(el)
      })
    }, { threshold: 0.12, rootMargin: '0px 0px -30px' })
    reveals.forEach(el => io.observe(el))
  }

  /* ---------- post: toc / progress / copy / tabs ---------- */

  const article = $('#articleContent')
  const tocNav = $('#tocNav')
  const tocMobile = $('#tocMobileNav')
  let headings = []

  if (article) {
    headings = $$('h2, h3', article).filter(h => h.textContent.trim())
    headings.forEach((h, i) => {
      if (!h.id) h.id = 'heading-' + (i + 1)
    })
    if (headings.length >= 2) {
      const items = headings.map(h => {
        const a = document.createElement('a')
        a.href = '#' + encodeURIComponent(h.id)
        a.textContent = h.textContent.trim()
        a.className = 'level-' + h.tagName.slice(1)
        a.addEventListener('click', e => {
          e.preventDefault()
          const target = document.getElementById(h.id)
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' })
            history.replaceState(null, '', '#' + encodeURIComponent(h.id))
            if (tocMobile && tocMobile.closest('details')) tocMobile.closest('details').open = false
          }
        })
        return a
      })
      if (tocNav) items.forEach(a => tocNav.appendChild(a.cloneNode(true)))
      if (tocMobile) items.forEach(a => tocMobile.appendChild(a))
      // clones need the same click behaviour
      $$('a', tocNav).forEach((a, i) => {
        a.addEventListener('click', e => {
          e.preventDefault()
          const h = headings[i]
          const target = document.getElementById(h.id)
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' })
            history.replaceState(null, '', '#' + encodeURIComponent(h.id))
          }
        })
      })
    } else {
      const card = $('#tocCard')
      if (card) card.style.display = 'none'
      const mob = $('#tocMobile')
      if (mob) mob.style.display = 'none'
    }

    // code copy
    $$('.code-copy', article).forEach(btn => {
      btn.addEventListener('click', async () => {
        const block = btn.closest('.code-block')
        const code = block && $('pre', block)
        if (!code) return
        const text = code.innerText
        try {
          await navigator.clipboard.writeText(text)
        } catch (e) {
          const ta = document.createElement('textarea')
          ta.value = text
          ta.style.position = 'fixed'
          ta.style.opacity = '0'
          document.body.appendChild(ta)
          ta.select()
          document.execCommand('copy')
          ta.remove()
        }
        btn.textContent = '已复制'
        btn.classList.add('is-copied')
        setTimeout(() => {
          btn.textContent = '复制'
          btn.classList.remove('is-copied')
        }, 1600)
      })
    })

    // tabs
    $$('.tabs', article).forEach(tabs => {
      const buttons = $$('.nav-tabs button', tabs)
      const panes = $$('.tab-item-content', tabs)
      buttons.forEach((btn, i) => {
        btn.addEventListener('click', () => {
          buttons.forEach(b => b.closest('.tab').classList.remove('active'))
          panes.forEach(p => p.classList.remove('active'))
          btn.closest('.tab').classList.add('active')
          if (panes[i]) panes[i].classList.add('active')
        })
      })
    })
  }

  const progressBar = $('#readingBar')
  function updateReading(y) {
    if (!progressBar || !article) return
    const rect = article.getBoundingClientRect()
    const start = window.scrollY + rect.top - 90
    const end = start + article.offsetHeight - window.innerHeight + 180
    const pct = end > start ? ((y - start) / (end - start)) * 100 : 0
    progressBar.style.width = Math.max(0, Math.min(100, pct)) + '%'
  }

  let activeToc = null
  function updateToc() {
    if (!headings.length || !tocNav) return
    const y = window.scrollY + 150
    let current = headings[0]
    for (const h of headings) {
      if (h.offsetTop <= y) current = h
      else break
    }
    const links = $$('a', tocNav)
    links.forEach(a => a.classList.remove('is-active'))
    const idx = headings.indexOf(current)
    if (links[idx]) {
      links[idx].classList.add('is-active')
      activeToc = links[idx]
    }
  }
  window.addEventListener('scroll', updateToc, { passive: true })

  // copy article link
  $$('[data-copy-url]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const span = $('span', btn)
      try {
        await navigator.clipboard.writeText(location.href)
      } catch (e) {
        const ta = document.createElement('textarea')
        ta.value = location.href
        ta.style.position = 'fixed'
        ta.style.opacity = '0'
        document.body.appendChild(ta)
        ta.select()
        document.execCommand('copy')
        ta.remove()
      }
      if (span) {
        const old = span.textContent
        span.textContent = '已复制'
        setTimeout(() => { span.textContent = old }, 1600)
      }
    })
  })

  /* ---------- misc ---------- */

  if (toTop) {
    $('button', toTop).addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }))
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
  updateToc()
})()
