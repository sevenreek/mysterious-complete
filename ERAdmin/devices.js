$(function(){

  window.setInterval(function(){
    loadLatestResults();
  }, 1000);

  function loadLatestResults(){

    $.ajax({
      url : 'http://localhost:8080/devices/list',
      cache : false,
      dataType : "text",
      success : function(data){
        $('#devices_foundcount').html(data);
      },
      error: function (error) {
        console.log("error:" + error);
      }
    });
  }

});
