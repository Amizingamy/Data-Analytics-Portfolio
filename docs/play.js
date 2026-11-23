(function(){
var FACTS={hamper:'<span><b>Fact 1.</b> Festive gifting hampers at The Brew Room brought in about ₹5 lakh.</span>',match:'<span><b>Fact 2.</b> I started out in culinary arts (BA, GPA 8.13) and moved into marketing and now data.</span>',quiz:'<span><b>Fact 3.</b> At Beyondskool I brought in ₹1 crore in four months and was #1 on the leaderboard in March 2022.</span>'};
var ORDER=['hamper','match','quiz'],done={};
function st(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
try{done=JSON.parse(st('unlocked')||'{}')||{}}catch(e){done={}}
function $(s,r){return (r||document).querySelector(s)}
function render(){var n=0;ORDER.forEach(function(k){var f=$('#f-'+k),open=!!done[k];if(open)n++;f.className='fact'+(open?' open':'');f.innerHTML=open?FACTS[k]:'<span class="lock" aria-hidden="true">🔒</span><span>Win to unlock a fact about me.</span>'});
 document.querySelectorAll('.prog i').forEach(function(i,x){i.classList.toggle('on',x<n)});$('#pc').textContent=n+' of 3 unlocked';
 var fin=$('#final');fin.classList.toggle('locked',n<3);$('#fc').hidden=n<3;$('#fh').textContent=n<3?'Final level: locked':'Level complete. Thanks for playing!';$('#fp').textContent=n<3?'Unlock all three facts to open the last level.':'If you liked how this was built, imagine what I could build for your brand. Let\'s talk.'}
function win(k){if(!done[k]){done[k]=1;st('unlocked',JSON.stringify(done))}render();var f=$('#f-'+k);f.scrollIntoView({block:'nearest',behavior:'smooth'})}
function stage(k){return $('#st-'+k)}
var timers={};function clr(k){(timers[k]||[]).forEach(function(t){clearInterval(t);clearTimeout(t)});timers[k]=[]}
function start(k){clr(k);timers[k]=[];var s=stage(k);s.innerHTML='';({hamper:hamper,match:match,quiz:quiz})[k](s,k)}
function hamper(s,k){var score=0,t=20;s.style.display='block';var hud=document.createElement('div');hud.className='hud';hud.innerHTML='<span id="hs">Caught: 0 / 8</span><span id="ht">20s</span>';s.appendChild(hud);
 function spawn(){var b=document.createElement('button');b.className='ham';b.setAttribute('aria-label','Catch hamper');b.textContent='🎁';b.style.left=(Math.random()*(s.clientWidth-50)+2)+'px';b.onclick=function(){score++;b.remove();$('#hs',s).textContent='Caught: '+score+' / 8';if(score>=8)end(true)};b.addEventListener('animationend',function(){b.remove()});s.appendChild(b)}
 var a=setInterval(spawn,650),c=setInterval(function(){t--;$('#ht',s).textContent=t+'s';if(t<=0)end(score>=8)},1000);timers[k].push(a,c);spawn();
 function end(w){clr(k);s.innerHTML='';s.style.display='grid';s.innerHTML=w?'<div><p style="font:400 2rem var(--serif)">You got them!</p><p>Fact unlocked below.</p></div>':'<div><p style="font:400 1.6rem var(--serif)">So close! You caught '+score+'.</p><p>Press Start to try again.</p></div>';if(w)win(k)}}
function match(s,k){s.style.display='block';var P=[['RFM','Who buys, how often, how much'],['K-means','Sorts customers into groups'],['p-value','Is the lift just luck?'],['SQL','Asks the data questions']],cards=[];
 P.forEach(function(p,i){cards.push({t:p[0],i:i});cards.push({t:p[1],i:i})});cards.sort(function(){return Math.random()-.5});
 var g=document.createElement('div');g.className='mg';var first=null,lock=false,m=0;
 cards.forEach(function(c){var b=document.createElement('button');b.setAttribute('aria-label','Hidden card');b.textContent='?';b.style.color='#fff';b.onclick=function(){if(lock||b.classList.contains('up')||b.classList.contains('ok'))return;b.classList.add('up');b.textContent=c.t;b.style.color='';b.setAttribute('aria-label',c.t);
  if(!first){first={b:b,c:c};return}
  if(first.c.i===c.i){first.b.classList.replace('up','ok');b.classList.replace('up','ok');first=null;m++;if(m===4){setTimeout(function(){s.innerHTML='<div style="display:grid;place-items:center;height:100%;min-height:200px"><div><p style="font:400 2rem var(--serif)">All matched!</p><p>Fact unlocked below.</p></div></div>';win(k)},500)}}
  else{lock=true;var f=first;first=null;timers[k].push(setTimeout(function(){[f.b,b].forEach(function(x){x.classList.remove('up');x.textContent='?';x.style.color='#fff';x.setAttribute('aria-label','Hidden card')});lock=false},900))}};g.appendChild(b)});
 s.appendChild(g)}
function quiz(s,k){s.style.display='block';var Q=[['How many brands did I work with at The Duchess Club?',['10+','50+','100+'],2],['How much did my Beyondskool sales team bring in over four months?',['₹10 lakh','₹1 crore','₹10 crore'],1],['How many SQL queries are in my Brew Room case study?',['5','12','30'],1]],i=0,sc=0;
 function show(){if(i>=Q.length){s.style.display='grid';s.innerHTML='<div><p style="font:400 2rem var(--serif)">'+sc+' out of 3!</p><p>Fact unlocked below.</p></div>';win(k);return}
  var q=Q[i];s.innerHTML='<div class="q"><p>'+(i+1)+'/3 · '+q[0]+'</p></div>';var w=$('.q',s);q[1].forEach(function(o,x){var b=document.createElement('button');b.textContent=o;b.onclick=function(){w.querySelectorAll('button').forEach(function(y){y.disabled=true});if(x===q[2]){sc++;b.classList.add('good')}else{b.classList.add('bad');w.querySelectorAll('button')[q[2]].classList.add('good')}timers[k].push(setTimeout(function(){i++;show()},900))};w.appendChild(b)})}
 show()}
document.addEventListener('click',function(e){var a=e.target.closest('[data-start]'),b=e.target.closest('[data-skip]');if(a)start(a.dataset.start);if(b){var k=b.dataset.skip;clr(k);stage(k).style.display='grid';stage(k).innerHTML='<div><p style="font:400 1.6rem var(--serif)">Skipped. No problem!</p><p>Fact unlocked below.</p></div>';win(k)}});
$('#reset').onclick=function(){done={};st('unlocked','{}');ORDER.forEach(function(k){clr(k);stage(k).innerHTML='';stage(k).style.display='grid'});render()};
render();
})();
