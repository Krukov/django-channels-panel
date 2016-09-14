(function ($) {
     // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var td = function (body) { return '<td>' + body + '</td>'; }

    // ***CONSUMERS***
    $('.consumer_content').each(function (i) {
        var $this = $(this);
        var group = $this.data('consumer-group')
        var socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/__debug__/join/" + group + "/");
        var odd = true;
        socket.onmessage = function(message) {
            var data = JSON.parse(message.data).data;
            // Handle errors
            $this.find('.no_content').remove()

            // Handle message
            var template = td(data.channel) + td(JSON.stringify(data.call_kwargs)) + td(JSON.stringify(data.message));
            var trClass = odd ? 'djDebugOdd' : 'djDebugEven';
            odd = !odd;
            $('<tr class="' + trClass + '">' + template + '</tr>').appendTo($this);
        };
        socket.onopen = function() { console.log("Connected to the debug group ", group); }
    })


    // ***GROUPS***
    var groupsSocket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/__debug__/join/debug.groups/");

    var GroupsOdd = true;

    groupsSocket.onmessage = function(message) {
        $('#groups_no_content').remove();
        var message = JSON.parse(message.data);
        var data = message.data;
        var event = message.event;
        var template = td(data.group) + td(event) + td(data.channel || JSON.stringify(data.content));
        var trClass = GroupsOdd ? 'djDebugOdd' : 'djDebugEven';
        GroupsOdd = !GroupsOdd;
        $('<tr class="' + trClass + '">' + template + '</tr>').appendTo('#groups_table');
    };

    groupsSocket.onopen = function() { console.log("Connected to the debug groups socket"); }

    // ***CHANNELS***
    var channelsSocket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/__debug__/join/debug.channels/");

    var channelsOdd = true;

    channelsSocket.onmessage = function(message) {
        $('#channels_no_content').remove();
        var message = JSON.parse(message.data);
        var data = message.data;
        var event = message.event;
        var template = td(data.channel) + td(event) + td(JSON.stringify(data.content));
        var trClass = channelsOdd ? 'djDebugOdd' : 'djDebugEven';
        channelsOdd = !channelsOdd;
        $('<tr class="' + trClass + '">' + template + '</tr>').appendTo('#channels_table');
    };

    channelsSocket.onopen = function() { console.log("Connected to the debug channels socket"); }
})(djdt.jQuery);