// Pointer-based drawing navigation, adapted to the existing gallery viewer.
function createDrawingPanZoom(viewport, picture, controls) {
  const state = { x: 0, y: 0, scale: 1 };
  const pointers = new Map();
  let travel = 0, multiple = false, lastTap = null;
  function paint() {
    picture.style.transform = `translate(${state.x}px, ${state.y}px) scale(${state.scale})`;
    controls.level.textContent = Math.round(state.scale * 100) + '%';
  }
  function reset() {
    Object.assign(state, { x: 0, y: 0, scale: 1 });
    pointers.clear(); lastTap = null;
    viewport.classList.remove('is-dragging'); paint();
  }
  function zoomAt(x, y, scale) {
    const next = Math.max(.5, Math.min(9, scale));
    const ratio = next / state.scale;
    state.x = x - (x - state.x) * ratio;
    state.y = y - (y - state.y) * ratio;
    state.scale = next;
  }
  function centerZoom(factor) {
    const rect = viewport.getBoundingClientRect();
    zoomAt(rect.width / 2, rect.height / 2, state.scale * factor); paint();
  }
  const local = e => {
    const rect = viewport.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };
  function pair() {
    const [a, b] = [...pointers.values()];
    return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, distance: Math.hypot(a.x - b.x, a.y - b.y) };
  }
  viewport.addEventListener('wheel', e => {
    e.preventDefault();
    const p = local(e), unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? viewport.clientHeight : 1;
    zoomAt(p.x, p.y, state.scale * Math.exp(-Math.max(-150, Math.min(150, e.deltaY * unit)) * .004)); paint();
  }, { passive: false });
  viewport.addEventListener('pointerdown', e => {
    if (e.button !== 0 && e.pointerType === 'mouse') return;
    if (!pointers.size) { travel = 0; multiple = false; }
    pointers.set(e.pointerId, local(e));
    if (pointers.size > 1) multiple = true;
    viewport.focus({ preventScroll: true });
    viewport.setPointerCapture(e.pointerId);
    viewport.classList.add('is-dragging');
  });
  viewport.addEventListener('pointermove', e => {
    const previous = pointers.get(e.pointerId); if (!previous) return;
    const before = pointers.size > 1 ? pair() : null, p = local(e);
    const dx = p.x - previous.x, dy = p.y - previous.y;
    travel += Math.abs(dx) + Math.abs(dy); pointers.set(e.pointerId, p);
    if (before) {
      const after = pair();
      if (before.distance > 1) zoomAt(before.x, before.y, state.scale * after.distance / before.distance);
      state.x += after.x - before.x; state.y += after.y - before.y;
    } else { state.x += dx; state.y += dy; }
    paint();
  });
  function end(e) {
    if (!pointers.has(e.pointerId)) return;
    pointers.delete(e.pointerId);
    if (!pointers.size) {
      viewport.classList.remove('is-dragging');
      if (e.type === 'pointerup' && e.pointerType === 'touch' && !multiple && travel < 6) {
        if (lastTap !== null && e.timeStamp - lastTap < 320) reset();
        else lastTap = e.timeStamp;
      } else lastTap = null;
    }
  }
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(type => viewport.addEventListener(type, end));
  viewport.addEventListener('dblclick', e => { e.preventDefault(); reset(); });
  viewport.addEventListener('dragstart', e => e.preventDefault());
  viewport.addEventListener('keydown', e => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const moves = { ArrowLeft: [-40, 0], ArrowRight: [40, 0], ArrowUp: [0, -40], ArrowDown: [0, 40] };
    if (moves[e.key]) { state.x += moves[e.key][0]; state.y += moves[e.key][1]; paint(); }
    else if (e.key === '+' || e.key === '=') centerZoom(1.25);
    else if (e.key === '-') centerZoom(.8);
    else if (e.key === '0' || e.key === 'Home') reset();
    else return;
    e.preventDefault(); e.stopPropagation();
  });
  controls.plus.addEventListener('click', () => centerZoom(1.25));
  controls.minus.addEventListener('click', () => centerZoom(.8));
  controls.reset.addEventListener('click', reset);
  paint();
  return { reset, state };
}
if (typeof module !== 'undefined' && module.exports) module.exports = createDrawingPanZoom;
