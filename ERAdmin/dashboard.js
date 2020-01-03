function pad3(num, size){ return ('000' + num).substr(-size); }
//var deviceIPs = ["192.168.0.145", "192.168.0.177"]; // probably load from cookies
var deviceIPs = ["192.168.0.145"]; // probably load from cookies
var devicesPort = 8080;
const TIMER_STATES = {
  NULL        : 0,
  READY       : 1,
  STARTED     : 2,
  RESUMED     : 3,
  PAUSED      : 4,
  STOPPED_END : 5,
  STOPPED_WIN : 6
}
var devices = [];
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
$(function(){

  window.setInterval(function(){
    getRoomsState();
  }, 1000);

  function getRoomsState(){
   
    for (deviceIndex = 0; deviceIndex < devices.length; deviceIndex++) // add all deviceIPs
    {
      (function(deviceIndex) {
        $.ajax({
          url : 'http://' + devices[deviceIndex][3] + ':' + devicesPort + '/timer/status',
          cache : false,
          dataType : "json",
          crossDomain : true,
          success : function(statusData){
            updateRoomState(deviceIndex,statusData);
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
          deviceIndexInDevicesArray = devices.length-1; // if the device exists load it into the devices array and add a card for it
          $('#connected-devices-list').append('\
            <div class="col-12 mb-2">\
              <div class="card border-left-success shadow h-100 py-2" id="dev'+deviceIndexInDevicesArray+'-card">\
                <div class="card-body">\
                  <div class="row no-gutters align-items-center">\
                    <div class="col-xl-1 col-md-2 col-xs-6 align-items-center">\
                      <div class="text-xs font-weight-bold text-primary text-uppercase " id="dev'+deviceIndexInDevicesArray+'-name">'+deviceID+'('+model+')'+'</div>\
                      <div class="h5 mb-0 font-weight-bold text-gray-800 my-1" id="dev'+deviceIndexInDevicesArray+'-primary">21:38</div>\
                      <div class="text-xs font-weight-bold text-secondary text-uppercase " id="dev'+deviceIndexInDevicesArray+'-times">##:##-##:##</div>\
                    </div>\
                    <div class="col-xl-11 col-md-10 col-xs-6 d-flex flex-row flex-wrap bd-highlight align-items-center">\
                      <div class="bd-highlight">\
                        <button href="#" class="btn btn-success btn-icon-split m-1" id="dev'+deviceIndexInDevicesArray+'-btn-play" disabled>\
                          <span class="icon text-white-50">\
                            <i class="fas fa-play"></i>\
                          </span>\
                          <span class="text" id="dev'+deviceIndexInDevicesArray+'-btn-play-text">Wznów</span>\
                        </button>\
                      </div>\
                      <div class="bd-highlight">\
                        <button href="#" class="btn btn-warning btn-icon-split m-1" id="dev'+deviceIndexInDevicesArray+'-btn-pause">\
                          <span class="icon text-white-50">\
                            <i class="fas fa-pause"></i>\
                          </span>\
                          <span class="text">Pauza</span>\
                        </button>\
                      </div>\
                      <div class="bd-highlight">\
                        <button href="#" class="btn btn-danger btn-icon-split m-1" id="dev'+deviceIndexInDevicesArray+'-btn-stop">\
                          <span class="icon text-white-50">\
                            <i class="fas fa-stop"></i>\
                          </span>\
                          <span class="text">Zakończ grę</span>\
                        </button>\
                      </div>\
                      <div class="border-left-info m-1 shadow form-inline d-inline-block pl-1">\
                        <input type="number" placeholder="MM" class="form-control input-lg text-center h-100 d-inline-block" style="width:5em;" id="dev'+deviceIndexInDevicesArray+'-btn-reset-val" value="60">\
                        <button href="#" class="btn btn-info btn-icon-split d-inline-block" id="dev'+deviceIndexInDevicesArray+'-btn-reset" disabled>\
                          <span class="icon text-white-50">\
                            <i class="fas fa-redo "></i>\
                          </span>\
                          <span class="text">Reset pokoju</span>\
                        </button>\
                      </div>\
                      <div class="border-left-secondary m-1 shadow form-inline d-inline-block pl-1">\
                        <input type="number" placeholder="MM" class="form-control input-lg text-center h-100 d-inline-block" style="width:5em;" id="dev'+deviceIndexInDevicesArray+'-btn-add-val" value="5">\
                        <a href="#" class="btn btn-secondary btn-icon-split d-inline-block" id="dev'+deviceIndexInDevicesArray+'-btn-add">\
                          <span class="icon text-white-50 ">\
                            <i class="fas fa-plus"></i>\
                          </span>\
                          <span class="text">Dodaj Czas</span>\
                        </a>\
                      </div>\
                    </div>\
                  </div>\
                </div>\
              </div>\
            </div>\
          ') // end device html card
          $('head').append("<script>\
          $('#dev"+deviceIndexInDevicesArray+"-btn-play').click({device: "+deviceIndexInDevicesArray+", command: '/timer/play'}, sendCommand);\
          $('#dev"+deviceIndexInDevicesArray+"-btn-pause').click({device: "+deviceIndexInDevicesArray+", command: '/timer/pause'}, sendCommand);\
          $('#dev"+deviceIndexInDevicesArray+"-btn-stop').click({device: "+deviceIndexInDevicesArray+", command: '/timer/stop'}, sendCommand);\
          $('#dev"+deviceIndexInDevicesArray+"-btn-reset').click(function() {\
            var secs = 60*parseInt($('#dev"+deviceIndexInDevicesArray+"-btn-reset-val').val());\
            sendCommandString(deviceIndexInDevicesArray,'/timer/reset?totalseconds='+secs);\
          });\
          $('#dev"+deviceIndexInDevicesArray+"-btn-add').click(function() {\
            var secs = 60*parseInt($('#dev"+deviceIndexInDevicesArray+"-btn-add-val').val());\
            sendCommandString(deviceIndexInDevicesArray,'/timer/add?totalseconds='+secs);\
          });\
          <\/script>");
        }, // end success
        error: function (xhr, status, error) {
          console.log("error:" + xhr.responseText);
        } // end error
      }); // end ajax anonymous function
    })(deviceIndex);
  } // end devices for loop
  
});
function sendCommandString(devindex, str)
{
  $.ajax({
    url : 'http://' + devices[devindex][3] + ':' + devicesPort + str,
    cache : false,
    dataType : "json",
    crossDomain : true/*,
    success : function(statusData){
      updateRoomState(deviceIndex,statusData);
    }*/
  });
}
function sendCommand(event)
{
  sendCommandString(event.data.device,event.data.command);
}
function updateRoomState(deviceIndex, statusData)
{
  var totalSeconds = parseInt(statusData[0]);
  var timerRunning = statusData[1];
  var deviceState = statusData[2];
  var minutes = ~~(totalSeconds / 60); // werid js integer division
  var seconds = totalSeconds - minutes*60;
  var countingDown = statusData[1];
  $('#dev' + deviceIndex + '-primary').html(pad3(minutes,2) + ":" + pad3(seconds,2));
  switch(deviceState) {
    case TIMER_STATES.READY:
      $("#dev" + deviceIndex + '-card').removeClass('border-left-danger');
      $("#dev" + deviceIndex + '-card').addClass('border-left-info');
      $("#dev" + deviceIndex + '-btn-play').prop("disabled", false);
      $("#dev" + deviceIndex + '-btn-pause').prop("disabled", true);
      $("#dev" + deviceIndex + '-btn-stop').prop("disabled", true);
      $("#dev" + deviceIndex + '-btn-reset').prop("disabled", false);
      $("#dev" + deviceIndex + '-btn-play-text').html("Rozpocznij grę");
    break;
    case TIMER_STATES.STARTED:
    case TIMER_STATES.RESUMED:
      $("#dev" + deviceIndex + '-card').removeClass('border-left-danger');
      $("#dev" + deviceIndex + '-card').removeClass('border-left-info');
      $("#dev" + deviceIndex + '-card').removeClass('border-left-warning');
      $("#dev" + deviceIndex + '-card').addClass('border-left-success');
      $("#dev" + deviceIndex + '-btn-play').prop("disabled", true);
      $("#dev" + deviceIndex + '-btn-pause').prop("disabled", false);
      $("#dev" + deviceIndex + '-btn-stop').prop("disabled", false);
      $("#dev" + deviceIndex + '-btn-reset').prop("disabled", true);
      $("#dev" + deviceIndex + '-btn-play-text').html("Wznów");
    break;
    case TIMER_STATES.PAUSED:
      $("#dev" + deviceIndex + '-card').removeClass('border-left-success');
      $("#dev" + deviceIndex + '-card').addClass('border-left-warning');
      $("#dev" + deviceIndex + '-btn-play').prop("disabled", false);
      $("#dev" + deviceIndex + '-btn-pause').prop("disabled", true);
      $("#dev" + deviceIndex + '-btn-stop').prop("disabled", false);
      $("#dev" + deviceIndex + '-btn-play-text').html("Wznów");
    break;
    case TIMER_STATES.STOPPED_END:
    case TIMER_STATES.STOPPED_WIN:
      $("#dev" + deviceIndex + '-card').removeClass('border-left-success');
      $("#dev" + deviceIndex + '-card').removeClass('border-left-info');
      $("#dev" + deviceIndex + '-card').removeClass('border-left-warning');
      $("#dev" + deviceIndex + '-card').addClass('border-left-danger');
      $("#dev" + deviceIndex + '-btn-play').prop("disabled", false);
      $("#dev" + deviceIndex + '-btn-pause').prop("disabled", true);
      $("#dev" + deviceIndex + '-btn-stop').prop("disabled", true);
      $("#dev" + deviceIndex + '-btn-reset').prop("disabled", false);
      $("#dev" + deviceIndex + '-btn-play-text').html("Wznów");
    break;
    default:
    break;
  }
}