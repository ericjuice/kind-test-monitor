var socket = io.connect('http://' + document.domain + ':' + location.port);
var connected = false
note = document.getElementById('notifyer');
statu_light = document.getElementById('status_light');

// a small colorful light hahahah
function setLightColorClass(color_class){
    statu_light.classList.forEach(className => {
        if (className.startsWith('bg-')) {
          statu_light.classList.remove(className);
        }
      });
      statu_light.classList.add(color_class);
}

socket.on('connect_error', function (error) {
    note.innerHTML = '连接失败' + error
    setLightColorClass('bg-red-300')
    console.log('连接失败:', error);
    socket.disconnect();
});

socket.on('err_msg', function (data) {
    note.innerHTML = data.data;
    console.log('错误:',data.data)
    setLightColorClass('bg-red-300')
})

// check connection
socket.on('connection_response', function (data) {
    if (data == 1) {
        note.innerHTML = '连接后端成功';
        setLightColorClass('bg-green-300')
        connected = true;
    } else {
        note.innerHTML = '连接后端失败';
        connected = false;
    }
    var max_retry = 0;
    var retryInterval = 1000; // 1秒

    function reconnect() {
        note.innerHTML = '正在重连';
        console.log('正在重连');
        setLightColorClass('bg-yellow-300')
        socket.emit('reconnect');
        max_retry += 1;
        if (max_retry > 10) {
            note.innerHTML = '重连失败';
            console.log('重连失败');
            return;
        }
        if (!connected) {
            setTimeout(reconnect, retryInterval);
        }
    }
    if (!connected) {
        setTimeout(reconnect, retryInterval);
    }

    console.log("connect status: ", data);
});


// when flame graph is ready
socket.on('flame_ok', function (data) {
    flame_res_div = document.getElementById('exec_gen_flame_res');
    flame_res_div.innerHTML = data.data;
    console.log("receive flame ok");
    // TODO : draw
});

// when test cmd is ok
socket.on('test_ok', function (data) {
    // id="exec_test_res"
    test_res_div = document.getElementById('exec_test_res');
    test_res_div.innerHTML = data.data;
    console.log("receive test ok");
    // TODO : text
})


// exec Test cmd through websocket
function submitTestForm(event) {
    event.preventDefault();
    // get args
    var time = document.getElementById('exec_test_time').value;
    var thread = document.getElementById('exec_test_thread').value;
    var qps = document.getElementById('exec_test_qps').value;
    var addr = document.getElementById('exec_test_addr').value;
    // emit args
    console.log("submit test", time, thread, qps, addr);
    socket.emit('exec_test_command', { 'time': time, 'thread': thread, 'qps': qps, 'addr': addr });
}

// exec Flame generating cmd through websocket
function submitFlameForm(event) {
    event.preventDefault();
    // get args
    var time = document.getElementById('exec_gen_flame_time').value;
    var hz = document.getElementById('exec_gen_flame_hz').value;
    var type = document.getElementById('exec_gen_flame_selector').value;
    // emit args
    console.log("submit flame", time, hz, type);
    socket.emit('exec_gen_flame', { 'time': time, 'hz': hz, 'type': type });
}


// exec all cmd on host through ajax
function submitExecForm(event) {
    event.preventDefault();
    var command = $("#exec_command_input").val();
    $.ajax({
        url: "/exec_cmd_by_post",
        type: "POST",
        data: { command: command },
        success: function (response) {
            $("#exec_cmd_result").html(response.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>'));
            // console.log(response);
        },
        error: function (error) {
            $("#exec_cmd_result").html(error);
            // console.log(error);
        }
    });
}