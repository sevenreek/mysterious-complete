function pad3(num, size){ return ('000' + num).substr(-size); }
var devicesPort = 8080;

const ROOM_STATES = {
  STATE_READY      : 0,
  STATE_RUNNING    : 1,
  STATE_PAUSED     : 2,
  STATE_STOPPED    : 3
}

$(function(){
  window.setInterval(function(){
    updateDevices();
  }, 1000);
});
$('[data-toggle="tooltip"]').tooltip();
$( document ).ready(function() {
  console.log(devices);
});
function updateDevices(){
  $.ajax({
    url : '/devices/raw',
    cache : false,
    dataType : "json",
    crossDomain : false,
    success : function(statusData){
      devices = statusData;
      updateRoomViews(devices);
    },
    error: function (xhr, status, error) {
      console.log("error:" + xhr.responseText);
    }
  });
}
function sendCommandString(devindex, str)
{
  $.ajax({
    url : '/devices/'+devindex+'/cmd/'+str,
    cache : false,
    dataType : "json",
    crossDomain : false
  });
}
function sendCommand(event)
{
  sendCommandString(event.data.device, event.data.command);
}
function playRoom(index)
{
  $.ajax({
    url : '/devices/'+index+'/play',
    cache : false,
    dataType : "json",
    crossDomain : false
  });
}
function pauseRoom(index)
{
  $.ajax({
    url : '/devices/'+index+'/pause',
    cache : false,
    dataType : "json",
    crossDomain : false
  });
}
function stopRoom(index)
{
  $.ajax({
    url : '/devices/'+index+'/stop',
    cache : false,
    dataType : "json",
    crossDomain : false
  });
}
function resetRoom(index, time)
{
  $.ajax({
    url : '/devices/'+index+'/reset?t='+time,
    cache : false,
    dataType : "json",
    crossDomain : false
  });
}
function setRoomTime(index, time)
{
  $.ajax({
    url : '/devices/'+index+'/set?t='+time,
    cache : false,
    dataType : "json",
    crossDomain : false
  });
}
function addRoomTime(index, time)
{
  $.ajax({
    url : '/devices/'+index+'/add?t='+time,
    cache : false,
    dataType : "json",
    crossDomain : false
  });
}
function updateRoomViews(devicelist)
{
  for(deviceIndex = 0; deviceIndex < devicelist.length; deviceIndex++)
  {
    device = devicelist[deviceIndex];
    var minutes = ~~(device.timeleft / 60); // werid js integer division
    var seconds = device.timeleft - minutes*60;
    $('#dev' + deviceIndex + '-primary').html(pad3(minutes,2) + ":" + pad3(seconds,2));
    switch(device.state) {
      case ROOM_STATES.STATE_READY:
        $("#dev" + deviceIndex + '-times').html("##:##" + "-" + "##:##");
        $("#dev" + deviceIndex + '-card').removeClass('border-left-danger');
        $("#dev" + deviceIndex + '-card').removeClass('border-left-warning');
        $("#dev" + deviceIndex + '-card').removeClass('border-left-success');
        $("#dev" + deviceIndex + '-card').addClass('border-left-info');
        $("#dev" + deviceIndex + '-btn-play').prop("disabled", false);
        $("#dev" + deviceIndex + '-btn-pause').prop("disabled", true);
        $("#dev" + deviceIndex + '-btn-stop').prop("disabled", true);
        $("#dev" + deviceIndex + '-btn-reset').prop("disabled", false);
        $("#dev" + deviceIndex + '-btn-play-text').html("Rozpocznij grę");
      break;
      case ROOM_STATES.STATE_RUNNING:
        $("#dev" + deviceIndex + '-times').html(startedOn + "-" + endsOn);
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
      case ROOM_STATES.STATE_PAUSED:
        $("#dev" + deviceIndex + '-times').html(startedOn + "-" + endsOn);
        $("#dev" + deviceIndex + '-card').removeClass('border-left-danger');
        $("#dev" + deviceIndex + '-card').removeClass('border-left-info');
        $("#dev" + deviceIndex + '-card').removeClass('border-left-success');
        $("#dev" + deviceIndex + '-card').addClass('border-left-warning');
        $("#dev" + deviceIndex + '-btn-play').prop("disabled", false);
        $("#dev" + deviceIndex + '-btn-pause').prop("disabled", true);
        $("#dev" + deviceIndex + '-btn-stop').prop("disabled", false);
        $("#dev" + deviceIndex + '-btn-play-text').html("Wznów");
      break;
      case ROOM_STATES.STATE_STOPPED:
        $("#dev" + deviceIndex + '-times').html("##:##" + "-" + "##:##");
        $("#dev" + deviceIndex + '-card').removeClass('border-left-info');
        $("#dev" + deviceIndex + '-card').removeClass('border-left-warning');
        $("#dev" + deviceIndex + '-card').removeClass('border-left-success');
        $("#dev" + deviceIndex + '-card').addClass('border-left-danger');
        $("#dev" + deviceIndex + '-btn-play').prop("disabled", true);
        $("#dev" + deviceIndex + '-btn-pause').prop("disabled", true);
        $("#dev" + deviceIndex + '-btn-stop').prop("disabled", true);
        $("#dev" + deviceIndex + '-btn-reset').prop("disabled", false);
        $("#dev" + deviceIndex + '-btn-play-text').html("Wznów");
      break;
      default:
      break;
    }
  }
}