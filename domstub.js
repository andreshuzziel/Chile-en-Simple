// Stub DOM mínimo para ejecutar los scripts del dashboard en Node.
class ClassList {
  constructor(){ this.s = new Set(); }
  add(...c){ c.forEach(x=>this.s.add(x)); }
  remove(...c){ c.forEach(x=>this.s.delete(x)); }
  toggle(c, f){ const on = f===undefined ? !this.s.has(c) : f; on ? this.s.add(c) : this.s.delete(c); return on; }
  contains(c){ return this.s.has(c); }
}
class El {
  constructor(id){
    this.id = id; this._html = ''; this._text = '';
    this.classList = new ClassList(); this.dataset = {}; this.style = {};
    this.value = ''; this.checked = false;
    this.children = [];
  }
  set innerHTML(v){ this._html = String(v); }
  get innerHTML(){ return this._html; }
  set textContent(v){ this._text = String(v); }
  get textContent(){ return this._text; }
  addEventListener(t, fn){ (this._ls ||= {})[t] = (this._ls[t]||[]).concat(fn); }
  fire(t, ev){ ((this._ls||{})[t]||[]).forEach(fn=>fn(ev||{})); }
  removeEventListener(){}
  querySelectorAll(){ return []; }
  querySelector(){ return null; }
  closest(){ return null; }
  appendChild(c){ this.children.push(c); return c; }
  remove(){}
  scrollIntoView(){}
  focus(){}
  getBoundingClientRect(){ return {top:0,left:0,width:100,height:100}; }
}
const cache = {};
function byId(id){ if(!cache[id]) cache[id] = new El(id); return cache[id]; }
global.document = {
  getElementById: byId,
  querySelector: (sel)=> byId(sel.replace(/^[#.]/,'')),
  querySelectorAll: ()=> [],
  createElement: (t)=> new El('dyn-'+t),
  addEventListener(){},
  body: new El('body'),
  documentElement: new El('html'),
};
global.window = global;
global.requestAnimationFrame = fn => fn();
global.location = { href: '' };
global.navigator = { clipboard: { writeText: async()=>{} } };
global.alert = ()=>{};
global.confirm = ()=> true;

module.exports = { byId, cache };
