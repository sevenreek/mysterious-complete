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
    url : '/room/raw',
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
    url : '/room/'+devindex+'/'+str,
    cache : false,
    dataType : "json",
    crossDomain : false
  });
}
function playRoom(index)
{
  sendCommandString(index, 'timer/play')
}
function pauseRoom(index)
{
  sendCommandString(index, 'timer/pause')
}
function stopRoom(index)
{
  sendCommandString(index, 'timer/stop')
}
function resetRoom(index, time)
{
  sendCommandString(index, 'timer/reset/' + time)
}
function setRoomTime(index, time)
{
  sendCommandString(index, 'timer/set/' + time)
}
function addRoomTime(index, time)
{
  sendCommandString(index, 'timer/add/' + time)
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