document.addEventListener('DOMContentLoaded',()=>{const slides=document.querySelectorAll('.slider .slide');const prevBtn=document.querySelector('.slider-prev');const nextBtn=document.querySelector('.slider-next');if(slides.length===0)return;let currentSlide=0;const slideInterval=5000;function showSlide(index){slides.forEach(slide=>{slide.classList.remove('active-slide');});slides[index].classList.add('active-slide');}
function nextSlide(){currentSlide=(currentSlide+1)%slides.length;showSlide(currentSlide);}
function prevSlide(){currentSlide=(currentSlide-1+slides.length)%slides.length;showSlide(currentSlide);}
if(nextBtn){nextBtn.addEventListener('click',()=>{nextSlide();clearInterval(autoSlide);autoSlide=setInterval(nextSlide,slideInterval);});}
if(prevBtn){prevBtn.addEventListener('click',()=>{prevSlide();clearInterval(autoSlide);autoSlide=setInterval(nextSlide,slideInterval);});}
showSlide(currentSlide);let autoSlide=setInterval(nextSlide,slideInterval);});