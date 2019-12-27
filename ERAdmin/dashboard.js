function pad3(num, size){ return ('000' + num).substr(-size); }
var deviceIPs = ["192.168.0.145", "192.168.0.177"]; // probably load from cookies
var devicesPort = 8080;
var devices = [];
var focusedDevice = null;
var linkedDeviceCount = 0;
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
    $('#device'+focusedDevice).removeClass('border-left-primary');
    $('#device'+focusedDevice).addClass('border-left-success');
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
      (function(deviceIndex) {
        $.ajax({
          url : 'http://' + devices[deviceIndex][3] + ':' + devicesPort + '/timer/status',
          cache : false,
          dataType : "json",
          crossDomain : true,
          success : function(statusData){
            //console.log(statusData);
            var totalSeconds = parseInt(statusData[0]);
            var minutes = ~~(totalSeconds / 60); // werid js integer division
            var seconds = totalSeconds - minutes*60;
            var countingDown = statusData[1];
            $('#dev' + deviceIndex + '-primary').html(pad3(minutes,2) + ":" + pad3(seconds,2));
            if(countingDown)
              $('#dev' + deviceIndex + '-ico').removeClass("invisible");
            else
              $('#dev' + deviceIndex + '-ico').addClass("invisible");
            if(focusedDevice != null && focusedDevice == deviceIndex)
            {
              $('#focused-device-primary').html(pad3(minutes,2) + ":" + pad3(seconds,2));
            }
          },
          error: function (xhr, status, error) {
            console.log("error:" + xhr.responseText);
          }
        });
      })(deviceIndex);
    }
    
  }

});


$( document ).ready(function() {
  var deviceIndex;
  for (deviceIndex = 0; deviceIndex < deviceIPs.length; deviceIndex++) // add all deviceIPs
  {
    (function(deviceIndex) {
      $.ajax({
        url : 'http://' + deviceIPs[deviceIndex] + ':' + devicesPort + '/who',
        cache : false,
        dataType : "json",
        crossDomain : true,
        success : function(statusData){
          //console.log(data);
          var deviceIP = deviceIPs[deviceIndex];
          devices.push(statusData.concat(deviceIP));
          var model = statusData[0];
          var tags = statusData[1];
          var deviceID = statusData[2];
          deviceIndexInDevicesArray = devices.length-1;
          $('#connected-devices-list').append('\
            <div class="col-xl-3 col-md-6 mb-4">\
              <a href="?focusDevice=' + deviceIndexInDevicesArray + '" class="card-clickable card border-left-primary shadow h-100 py-2" id="device'+deviceIndexInDevicesArray+'">\
                <div class="card-body">\
                  <div class="row no-gutters align-items-center">\
                    <div class="col mr-2">\
                      <div class="text-xs font-weight-bold text-primary text-uppercase mb-1" id="dev' + deviceIndexInDevicesArray + '-name"></div>\
                      <div class="h5 mb-0 font-weight-bold text-gray-800" id="dev' + deviceIndexInDevicesArray + '-primary">##:##</div>\
                    </div>\
                    <div class="col-auto invisible" id="dev' + deviceIndexInDevicesArray + '-ico">\
                      <i class="fas fa-stopwatch fa-2x text-gray-300"></i>\
                    </div>\
                  </div>\
                </div>\
              </a>\
            </div>\
          ')
          $('#dev'+deviceIndexInDevicesArray+'-name').html(deviceID + " (" + model + ")");
          linkedDeviceCount++;
          if(linkedDeviceCount == deviceIPs.length)
            fillFocusedDevice();
        },
        error: function (xhr, status, error) {
          console.log("error:" + xhr.responseText);
        }
      });
    })(deviceIndex);
  }
  
});
$('#fd-btn-resume').click({command: 'resume'}, focusedDeviceTimerControl);
$('#fd-btn-add5').click({command: 'add?totalseconds=300'}, focusedDeviceTimerControl);
$('#fd-btn-pause').click({command: 'pause'}, focusedDeviceTimerControl);
$('#fd-btn-set').click(focusedDeviceTimerSet);
function focusedDeviceTimerControl(event)
{
  $.ajax({
    url : 'http://' + devices[focusedDevice][3] + ':' + devicesPort + '/timer/' + event.data.command,
    cache : false,
    dataType : "json",
    crossDomain : true
  });
}
function focusedDeviceTimerSet(event)
{
  inputString = $("#timeset-value").val();
  var exp = RegExp("[0-9][0-9]:[0-9][0-9]");
  if(!exp.test(inputString))
  {
    alert("Format required: MM:SS!");
    return;
  }
  splitString = inputString.split(":");
  totalSeconds = parseInt(splitString[0])*60+parseInt(splitString[1]);
  console.log(totalSeconds);
  $.ajax({
    url : 'http://' + devices[focusedDevice][3] + ':' + devicesPort + '/timer/set?totalseconds=' + totalSeconds,
    cache : false,
    dataType : "json",
    crossDomain : true
  });
}