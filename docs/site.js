/* shared behaviour: reveal on scroll, lightbox, gallery filters */
document.documentElement.classList.add('js');
(function(){
  var els=document.querySelectorAll('.rv');
  if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in')});}
  else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.08});els.forEach(function(e){io.observe(e)});}
  var lb=document.getElementById('lb');
  if(lb){
    document.addEventListener('click',function(e){
      var im=e.target.closest('.shot img,.proof img');
      if(im){lb.querySelector('img').src=im.src;lb.querySelector('img').alt=im.alt;lb.querySelector('p').textContent=im.alt;lb.classList.add('open');return}
      if(lb.classList.contains('open'))lb.classList.remove('open');
    });
    addEventListener('keydown',function(e){if(e.key==='Escape')lb.classList.remove('open')});
  }
  var f=document.getElementById('filters');
  if(f){f.addEventListener('click',function(e){var b=e.target.closest('.f');if(!b)return;
    f.querySelectorAll('.f').forEach(function(x){x.setAttribute('aria-pressed',x===b)});
    document.querySelectorAll('#gal .shot').forEach(function(s){s.hidden=!(b.dataset.c==='all'||s.dataset.c===b.dataset.c)})})}
  function openHash(){var h=location.hash&&document.getElementById(location.hash.slice(1));if(h){var d=h.closest('details');if(d){d.open=true;h.scrollIntoView()}}}
  openHash();addEventListener('hashchange',openHash);
})();
