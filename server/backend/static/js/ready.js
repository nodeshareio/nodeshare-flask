
  function ready(callback){
    // in case the document is already rendered
    if (document.readyState!='loading') callback();
    // modern browsers
    else if (document.addEventListener) document.addEventListener('DOMContentLoaded', callback);
    // IE <= 8
    else document.attachEvent('onreadystatechange', function(){
        if (document.readyState=='complete') callback();
    });
}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}


ready(function(){
  var videos = document.getElementsByClassName("video-play"); 
  let i = 0;
  for (i=0; i < videos.length; i++ ){
    videos[i].loop = true;
    videos[i].muted = true;  
    videos[i].play(); 
  };

  if (document.querySelector('.fadeout')){
  document.querySelector('.fadeout').addEventListener("click", function(e){
    var removeTarget = e.target.parentNode;
    removeTarget.style.opacity = '0';
  });
};

  document.querySelector('.vid').addEventListener("click", function(e){

      if (e.target.paused){
        e.target.play();
      }
      else{
      e.target.pause();
    };
  });


});

