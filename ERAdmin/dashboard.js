$(function(){

  window.setInterval(function(){
    loadLatestResults();
  }, 1000);

  function loadLatestResults(){

    $.ajax({
      url : 'localhost:8080/devices/list',
      cache : false,
      crossDomain : true,
      dataType : "text",
      success : function(data){
        console.log("success")
        $('#devices_foundcount').html(data);
      },
      error: function (error) {
        console.log("error:" + error);
      }
    });
  }

});