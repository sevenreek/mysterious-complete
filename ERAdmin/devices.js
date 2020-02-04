var useAutomaticDeviceDetection = true;
var staticDeviceIPs = ["192.168.0.107","192.168.0.187","192.168.0.190"]; // probably load from cookies
var dynamicDeviceIPs = [];
var devicesPort = 8080;
var selectedDevice = -1;
var devices = [];
/*
( 
  name,
  ID,
  model,
  IP
)
*/
function sendCommandString(devindex, str)
{
  //alert('http://' + devices[devindex][3] + ':' + devicesPort + str);
  $.ajax({
    url : 'http://' + devices[devindex][3] + ':' + devicesPort + str,
    cache : false,
    dataType : "json",
    crossDomain : true
  });
}
function updateSelectedDevice(selection)
{
  
  selectedDevice = selection;
  console.log("Updating with "+devices[selectedDevice]);
  $('#cdev-id').html(devices[selectedDevice][1].toString(16));
  $('#cdev-ip').html(devices[selectedDevice][3]);
}
function sendCommandStringToAll(cmd)
{
  devices.forEach( dev =>
    {(function(dev) {
      $.ajax({
        url : 'http://' + dev[3] + ':' + devicesPort.toString() + cmd,
        cache : false,
        dataType : "json",
        crossDomain : true,
      }); // end ajax anonymous function
    })(dev);});
}
$('#global-reboot').on('click', function()
{
  sendCommandStringToAll('/reboot');
});
$('#global-shutdown').on('click', function()
{
  sendCommandStringToAll('/shutdown');
});
$('#global-sync').on('click', function()
{
  timestr = new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric"});
  sendCommandStringToAll('/link?time='+timestr);
});
$('[data-toggle="tooltip"]').tooltip();
$("#use-auto-ip").change(function()
{
  useAutomaticDeviceDetection = this.checked;
  dumpDeviceList();
  populateDeviceList(useAutomaticDeviceDetection);
});
$("#unlock-globals").change(function()
{
  if(this.checked)
  {
    $("#global-reboot").prop("disabled", false);
    $("#global-shutdown").prop("disabled", false);
    $("#global-sync").prop("disabled", false);
    
  }
  else
  {
    $("#global-reboot").prop("disabled", true);
    $("#global-shutdown").prop("disabled", true);
    $("#global-sync").prop("disabled", true);
  }
});
$('#devices-sel').on('change', function() {
  updateSelectedDevice($("#devices-sel option:selected").val());
});/*
$('#cdev-btn-setdeftime').on('click', function() {
  deftime = $('#cdev-btn-setdeftime-val').val();
  sendCommandString(selectedDevice, '/timer/setdefault?val='+deftime);
});*/
$('#cdev-btn-sync').on('click', function() {
  timestr = new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric"});
  sendCommandString(selectedDevice, '/link?time='+timestr);
});
$('#cdev-btn-shutdown').on('click', function() {
  sendCommandString(selectedDevice, '/shutdown');
});
$('#cdev-btn-reboot').on('click', function() {
  sendCommandString(selectedDevice, '/reboot');
});
$( document ).ready(function() {
  useAutomaticDeviceDetection = $("#use-auto-ip").is(":checked");
  populateDeviceList(useAutomaticDeviceDetection);
  
});
function appendDeviceFromJSON(jsonfile, ip)
{
  devices.push(jsonfile.concat(ip)); // add ip addr to the device json since /who does not return it
  var deviceName = jsonfile[0];
  var deviceID = jsonfile[1];
  var model = jsonfile[2];
  deviceIndexInDevicesArray = devices.length-1; // if the device exists load it into the devices array and add a card for it
  $('#devices-sel').append(
    '<option value="'+ deviceIndexInDevicesArray +'">'+ deviceName +'</option>'
  );
  if(deviceIndexInDevicesArray==0)
  {
    updateSelectedDevice(0);
  }
}
function populateDeviceList(automatic)
{
  if(automatic)
  {
    populateDynamicDeviceList();
  } 
  else 
  {
    populateStaticDeviceList();
  } // end if
}
function populateStaticDeviceList()
{
  var deviceIndex;
  for (deviceIndex = 0; deviceIndex < staticDeviceIPs.length; deviceIndex++) // add all deviceIPs
  {
    (function(deviceIndex) {
      $.ajax({
        url : 'http://' + staticDeviceIPs[deviceIndex] + ':' + devicesPort + '/who',
        cache : false,
        dataType : "json",
        crossDomain : true,
        success : function(statusData){
          var deviceIP = staticDeviceIPs[deviceIndex];
          appendDeviceFromJSON(statusData, deviceIP)
        }, // end success
        error: function (xhr, status, error) {
          console.log("error:" + xhr.responseText);
        } // end error
      }); // end ajax anonymous function
    })(deviceIndex);
  } // end devices for loop
}
function populateDynamicDeviceList()
{
  $.ajax({
    url : '/devices/list',
    cache : false,
    dataType : "json",
    success : function(ips){
      ips.forEach(ip => {
        (function(ip) {
          $.ajax({
            url : 'http://' + ip + ':' + devicesPort + '/who',
            cache : false,
            dataType : "json",
            crossDomain : true,
            success : function(statusData){
              appendDeviceFromJSON(statusData, ip)
            }, // end success
            error: function (xhr, status, error) {
              console.log("error:" + xhr.responseText);
            } // end error
          }); // end ajax anonymous function
        })(ip);
      });
    }
  });
}
function dumpDeviceList()
{
  $('#devices-sel').empty()
}