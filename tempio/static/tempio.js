function upload(file, single, redirect) {
    var signal = $.Deferred();
    var formData = new FormData();
    formData.append("file", file);

    var xhr = new XMLHttpRequest();

    /*
    if(settings.progress) {
        xhr.upload.addEventListener('progress', function(evt) {
            if(evt.lengthComputable) {
                var percentComplete = 100.0 * evt.loaded / evt.total;
                settings.progress(percentComplete);
            }
        }, false);
    }
    */

    xhr.onload = function(evt) {
        var data = JSON.parse(xhr.responseText);
        if (redirect && data.url) {
            window.location.href = single ? data.url : "/";
        }
    };

    xhr.open("POST", "/upload/", true);
    xhr.send(formData);

    return signal;
}

function uploadFiles(files) {
    let chain = null;
    let single = files.length == 1;
    // Call all the upload methods sequentially.
    for (var i = 0; i < files.length; i++) {
        let redirect = single || i == files.length - 1;
        chain = chain ? chain.then(upload(files[i], single, redirect)) : upload(files[i], single, redirect);
    }
    return chain;
}

$("html").on({
    dragover: function(e) {
        $(this).addClass("hover");
        return false;
    },
    "dragend dragleave": function(e) {
        $(this).removeClass("hover");
        return false;
    },
    drop: function(e) {
        e.preventDefault();
        $(this).removeClass("hover");
        uploadFiles(e.originalEvent.dataTransfer.files);
        return false;
    }
});
