function pad3(num, size){ return ('000' + num).substr(-size); }
var deviceIPs = ["192.168.0.145"]; // probably load from cookies
var devicesPort = 8080;
var devices = [];
var focusedDevice = null;
var getUrlParameter = function getUrlParameter(sParam) {
  var sPageURL = window.location.search.substring(1),
      sURLVariables = sPageURL.split('&'),
      sParameterName,
      i;

  for (i = 0; i < sURLVariables.length; i++) {
      sParameterName = sURLVariables[i].split('=');

      if (sParameterName[0] === sParam) {
          return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
      }
  }
  return null;
};
function fillFocusedDevice()
{
  focusedDevice = getUrlParameter('focusDevice');
  if(focusedDevice == null)
  {
    $('#focused-device-card').addClass('invisible');
  }
  else
  {
    $('#focused-device-card').removeClass('invisible');
    $('#focused-device-name').html(devices[parseInt(focusedDevice)][2]);
  }
}
$(function(){

  window.setInterval(function(){
    loadLatestResults();
  }, 1000);

  function loadLatestResults(){
    for (deviceIndex = 0; deviceIndex < deviceIPs.length; deviceIndex++) // add all deviceIPs
    {
      var localIndex = deviceIndex;
      $.ajax({
        url : 'http://' + deviceIPs[localIndex] + ':' + devicesPort + '/timer/status',
        cache : false,
        dataType : "json",
        crossDomain : true,
        success : function(statusData){
          //console.log(statusData);
          var totalSeconds = parseInt(statusData[0]);
          var minutes = ~~(totalSeconds / 60); // werid js integer division
          var seconds = totalSeconds - minutes*60;
          var countingDown = statusData[1];
          $('#dev' + localIndex + '-primary').html(pad3(minutes,2) + ":" + pad3(seconds,2));
          if(countingDown)
            $('#dev' + localIndex + '-ico').removeClass("invisible");
          else
            $('#dev' + localIndex + '-ico').addClass("invisible");
          if(focusedDevice != null && focusedDevice == localIndex)
          {
            $('#focused-device-primary').html(pad3(minutes,2) + ":" + pad3(seconds,2));
          }
        },
        error: function (xhr, status, error) {
          console.log("error:" + xhr.responseText);
        }
      });
    }
  }

});


$( document ).ready(function() {
  var deviceIndex;
  for (deviceIndex = 0; deviceIndex < deviceIPs.length; deviceIndex++) // add all deviceIPs
  {
    var localIndex = deviceIndex;
    $.ajax({
      url : 'http://' + deviceIPs[deviceIndex] + ':' + devicesPort + '/who',
      cache : false,
      dataType : "json",
      crossDomain : true,
      success : function(statusData){
        //console.log(data);
        devices.push(statusData);
        var model = statusData[0];
        var tags = statusData[1];
        var deviceID = statusData[2];
        $('#connected-devices-list').append('\
          <div class="col-xl-3 col-md-6 mb-4">\
            <a href="?focusDevice=' + localIndex + '" class="card-clickable card border-left-primary shadow h-100 py-2">\
              <div class="card-body">\
                <div class="row no-gutters align-items-center">\
                  <div class="col mr-2">\
                    <div class="text-xs font-weight-bold text-primary text-uppercase mb-1" id="dev' + localIndex + '-name"></div>\
                    <div class="h5 mb-0 font-weight-bold text-gray-800" id="dev' + localIndex + '-primary">##:##</div>\
                  </div>\
                  <div class="col-auto" id="dev' + localIndex + '-ico">\
                    <i class="fas fa-stopwatch fa-2x text-gray-300"></i>\
                  </div>\
                </div>\
              </div>\
            </a>\
          </div>\
        ')
        $('#dev0-name').html(deviceID + " (" + model + ")");
        if(localIndex == deviceIPs.length - 1)
          fillFocusedDevice();
      },
      error: function (xhr, status, error) {
        console.log("error:" + xhr.responseText);
      }
    });
    
  }
  
});
$('#fd-btn-resume').click({deviceIndex: focusedDevice, command: 'resume'}, focusedDeviceTimerControl);
$('#fd-btn-add5').click({deviceIndex: focusedDevice, command: 'add?totalseconds=300'}, focusedDeviceTimerControl);
function focusedDeviceTimerControl(event)
{
  $.ajax({
    url : 'http://' + deviceIPs[focusedDevice] + ':' + devicesPort + '/timer/' + event.data.command,
    cache : false,
    dataType : "html",
    crossDomain : true
  });
}