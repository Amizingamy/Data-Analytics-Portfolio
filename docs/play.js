(function(){
var KEY='unlocked2',done={},ORDER=['hamper','words','spot','maze','memory'],T={};
function sv(v){try{if(v===undefined)return localStorage.getItem(KEY);localStorage.setItem(KEY,v)}catch(e){return null}}
try{done=JSON.parse(sv()||'{}')||{}}catch(e){done={}}
function $(s,r){return(r||document).querySelector(s)}
function $$(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))}
var PAL={H:'#2A1618',S:'#EDBB9C',R:'#D9281C',G:'#C9973D',P:'#F4A3A3',M:'#B01E14',B:'#3B2A5C',y:'#FFD84D'};
function svg(rows,n,sc){var w=n||Math.max.apply(null,rows.map(function(r){return r.length})),o='<svg viewBox="0 0 '+w+' '+rows.length+'" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">';rows.forEach(function(r,y){for(var x=0;x<r.length;x++){var c=PAL[r[x]];if(c)o+='<rect x="'+x+'" y="'+y+'" width="1.02" height="1.02" fill="'+c+'"/>'}});return o+'</svg>'}
var GIRL=['................','.....HHHHHH.....','....HHHHHHHH....','...HHHHHHHHHH...','...HHSSSSSSHH...','...HHSSSSSSHH...','...HHSHSSHSHH...','...GHSSSSSSHG...','...HHPSMMSPHH...','...HHHSSSSHHH...','...HHHHSSHHHH...','....HHRRRRHH....','...HRRRRRRRRH...','..SRRRRRRRRRRS..','..SRRRRRRRRRRS..','...RRRRRRRRRR...','...RRRRRRRRRR...','....BBBBBBBB....','....BBB..BBB....','....BBB..BBB....'];
var GIFT=['..R..R..','...RR...','yyyRRyyy','yyyRRyyy','RRRRRRRR','yyyRRyyy','yyyRRyyy','yyyRRyyy'];
function render(){var n=0;ORDER.forEach(function(k){var o=!!done[k],r=$('#rw-'+k);if(o)n++;r.classList.toggle('locked',!o);r.classList.toggle('open',o);$('.st',r).textContent=o?'UNLOCKED':'LOCKED';});
$('#hp i').style.width=(n*20)+'%';$('#xp').textContent=n;
var w=$('#win');$('#wc').hidden=n<5;$('#wp').hidden=n>=5}
function win(k,quiet){var was=done[k];done[k]=1;sv(JSON.stringify(done));render();if(!quiet||!was){var r=$('#rw-'+k);r.scrollIntoView({block:'center',behavior:'smooth'})}}
function clr(k){(T[k]||[]).forEach(function(t){clearInterval(t);clearTimeout(t)});T[k]=[];if(T[k+'kd']){document.removeEventListener('keydown',T[k+'kd']);T[k+'kd']=null}}
function msg(s,a,b){s.className='stage';s.innerHTML='<div><p class="big">'+a+'</p><p>'+b+'</p></div>'}
function start(k){clr(k);var s=$('#st-'+k);s.className='stage';s.innerHTML='';T[k]=[];({hamper:hamper,words:words,spot:spot,maze:maze,memory:memory})[k](s,k)}
function hamper(s,k){var sc=0,t=20;s.className='stage top';s.innerHTML='<div class="hud2"><span id="hs">CAUGHT 0/8</span><span id="ht">20s</span></div>';
function end(w){clr(k);if(w){msg(s,'LEVEL CLEAR!','Loot unlocked below.');win(k)}else msg(s,'SO CLOSE! '+sc+'/8','Press Start to try again.')}
function sp(){var b=document.createElement('button');b.className='ham';b.setAttribute('aria-label','Catch hamper');b.innerHTML=svg(GIFT,8);b.style.left=Math.random()*Math.max(10,s.clientWidth-56)+'px';b.onclick=function(){sc++;b.remove();$('#hs',s).textContent='CAUGHT '+sc+'/8';if(sc>=8)end(true)};b.addEventListener('animationend',function(){b.remove()});s.appendChild(b)}
T[k].push(setInterval(sp,620),setInterval(function(){t--;var e=$('#ht',s);if(e)e.textContent=t+'s';if(t<=0)end(sc>=8)},1000));sp()}
function words(s,k){var G=[],L='SQLRFMBEAUCDKNOP',i;for(i=0;i<8;i++){G.push([]);for(var j=0;j<8;j++)G[i].push(L[(i*5+j*3+i*j)%L.length])}
function put(w,r,c,dr,dc){for(var i=0;i<w.length;i++)G[r+dr*i][c+dc*i]=w[i]}
put('TABLEAU',0,0,0,1);put('POWERBI',0,7,1,0);put('PYTHON',3,1,0,1);put('SQL',5,1,0,1);put('RFM',7,2,0,1);
var W=['TABLEAU','POWERBI','PYTHON','SQL','RFM'],found={},first=null;s.className='stage top';
var h='<div class="ws">';for(var r=0;r<8;r++)for(var c=0;c<8;c++)h+='<button data-r="'+r+'" data-c="'+c+'" aria-label="Letter '+G[r][c]+'">'+G[r][c]+'</button>';
h+='</div><div class="wl">'+W.map(function(w){return'<span id="w-'+w+'">'+w+'</span>'}).join('')+'</div>';s.innerHTML=h;
s.onclick=function(e){var b=e.target.closest('.ws button');if(!b)return;var r=+b.dataset.r,c=+b.dataset.c;
if(!first){first={r:r,c:c,b:b};b.classList.add('sel');return}
var dr=r-first.r,dc=c-first.c,n=Math.max(Math.abs(dr),Math.abs(dc)),cells=[];first.b.classList.remove('sel');
if(n>0&&(dr===0||dc===0||Math.abs(dr)===Math.abs(dc))){var sr=Math.sign(dr),sc=Math.sign(dc),str='';for(var i=0;i<=n;i++){var rr=first.r+sr*i,cc=first.c+sc*i;str+=G[rr][cc];cells.push($('.ws button[data-r="'+rr+'"][data-c="'+cc+'"]',s))}
var rev=str.split('').reverse().join(''),m=W.filter(function(w){return(w===str||w===rev)&&!found[w]})[0];
if(m){found[m]=1;cells.forEach(function(x){x.classList.add('hit')});$('#w-'+m,s).classList.add('f');if(Object.keys(found).length===5){setTimeout(function(){msg(s,'LEVEL CLEAR!','Loot unlocked below.');win(k)},500)}}}
first=null}}
var PA=['................','..cccc.....uu...','...cc......uu...','......rr....ll..','.....rrrr..llll.','....rrrrrr.llll.','....hhhhhh..tt..','....hwhhwh..tt..','....hhddhh..tt..','....hhddhh.f..f.','gggggggggggggggg','gggggggggggggggg'];
function spot(s,k){var P={c:'#D9C8FF',u:'#FFE45E',r:'#FF2E93',l:'#2E9A4C',h:'#E8C48F',w:'#5CC8FF',d:'#8B5A3C',t:'#8B5A3C',f:'#F4A3A3',g:'#2EE59D',y:'#FFD84D','.':'#1E1B4B'};
var B=PA.map(function(r){return r.split('')});B[2][3]='.';B[2][4]='.';B[7][8]='y';B[9][14]='.';
var D=[[2,3],[7,8],[9,14]],hit={};s.className='stage';
function scene(rows,iv){var o='<div class="scn" '+(iv?'data-b="1"':'')+'>';rows.forEach(function(r,y){r.forEach(function(c,x){o+='<i data-x="'+x+'" data-y="'+y+'" style="background:'+P[c]+'"></i>'})});return o+'</div>'}
s.innerHTML='<div style="width:100%"><div class="spp">'+scene(PA.map(function(r){return r.split('')}))+scene(B,1)+'</div><p id="sf" style="margin:10px 0 0">Found 0 of 3</p></div>';
s.onclick=function(e){var c=e.target.closest('.scn i');if(!c)return;var x=+c.dataset.x,y=+c.dataset.y;D.forEach(function(d,i){if(!hit[i]&&Math.abs(d[0]-y)<=1&&Math.abs(d[1]-x)<=1){hit[i]=1;$$('.scn i[data-x="'+d[1]+'"][data-y="'+d[0]+'"]',s).forEach(function(q){q.classList.add('found')})}});
var n=Object.keys(hit).length;$('#sf',s).textContent='Found '+n+' of 3';if(n===3)setTimeout(function(){msg(s,'LEVEL CLEAR!','Loot unlocked below.');win(k)},600)}}
var MZ=['###########','#S..#.....#','#.#.#.###.#','#.#...#...#','#.#####.#.#','#.....#.#.#','#####.#.#.#','#.....#...#','#.#######E#'];
function maze(s,k){var py=1,px=1;s.className='stage';
function draw(){var o='<div><div class="mz" style="grid-template-columns:repeat(11,1fr)" role="img" aria-label="Maze">';MZ.forEach(function(r,y){for(var x=0;x<11;x++){var c=r[x],bg=c==='#'?'#6A6BFF':'#14123A';if(y===py&&x===px)bg='#2EE59D';else if(c==='E')bg='#FFE45E';o+='<i style="background:'+bg+'"></i>'}});
o+='</div><div class="dpad"><span></span><button data-d="u" aria-label="Up">↑</button><span></span><button data-d="l" aria-label="Left">←</button><button data-d="d" aria-label="Down">↓</button><button data-d="r" aria-label="Right">→</button></div></div>';s.innerHTML=o}
function mv(d){var dy=d==='u'?-1:d==='d'?1:0,dx=d==='l'?-1:d==='r'?1:0,ny=py+dy,nx=px+dx;if(MZ[ny]&&MZ[ny][nx]&&MZ[ny][nx]!=='#'){py=ny;px=nx;draw();if(MZ[py][px]==='E'){clr(k);setTimeout(function(){msg(s,'LEVEL CLEAR!','Loot unlocked below.');win(k)},300)}}}
draw();s.onclick=function(e){var b=e.target.closest('.dpad button');if(b)mv(b.dataset.d)};
T[k+'kd']=function(e){var m={ArrowUp:'u',ArrowDown:'d',ArrowLeft:'l',ArrowRight:'r'}[e.key];if(m){e.preventDefault();mv(m)}};document.addEventListener('keydown',T[k+'kd'])}
function memory(s,k){var P=[['RFM','Who buys, how often, how much'],['K-means','Sorts customers into groups'],['p-value','Is the lift just luck?'],['SQL','Asks the data questions']],cs=[],first=null,lock=false,m=0;
P.forEach(function(p,i){cs.push([p[0],i]);cs.push([p[1],i])});cs.sort(function(){return Math.random()-.5});s.className='stage';var g=document.createElement('div');g.className='mg';
cs.forEach(function(c){var b=document.createElement('button');b.textContent='?';b.setAttribute('aria-label','Hidden card');b.onclick=function(){if(lock||b.classList.contains('up')||b.classList.contains('ok'))return;b.classList.add('up');b.textContent=c[0];if(!first){first={b:b,i:c[1]};return}
if(first.i===c[1]){first.b.classList.replace('up','ok');b.classList.replace('up','ok');first=null;m++;if(m===4)setTimeout(function(){msg(s,'LEVEL CLEAR!','Loot unlocked below.');win(k)},500)}
else{lock=true;var f=first;first=null;T[k].push(setTimeout(function(){[f.b,b].forEach(function(x){x.classList.remove('up');x.textContent='?'});lock=false},900))}};g.appendChild(b)});s.innerHTML='';s.appendChild(g)}
document.addEventListener('click',function(e){var a=e.target.closest('[data-start]'),b=e.target.closest('[data-skip]');if(a)start(a.dataset.start);if(b){var k=b.dataset.skip;clr(k);msg($('#st-'+k),'SKIPPED','Loot unlocked below.');win(k)}});
$$('#reset,.rs').forEach(function(x){x.onclick=function(){done={};sv('{}');ORDER.forEach(function(k){clr(k);var s=$('#st-'+k);s.className='stage';s.innerHTML='';s.onclick=null});render();window.scrollTo({top:0,behavior:'smooth'})}});
ORDER.forEach(function(k){$('#st-'+k).innerHTML='<p>Press Start to play</p>'});render();
})();
