$(function(){

  window.setInterval(function(){
    loadLatestResults();
  }, 1000);

  function loadLatestResults(){

    $.ajax({
      url : 'http://192.168.0.145:8080/timer/status',
      cache : false,
      dataType : "json",
      success : function(data){
        $('#dev1-primary').html(data);
      },
      error: function (error) {
        console.log("error:" + error);
      }
    });
  }

});
