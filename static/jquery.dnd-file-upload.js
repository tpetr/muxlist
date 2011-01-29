(function($) {

	var opts = {};

	var last_file = null;

	$.fn.getURL = function () { return opts.url; }
	$.fn.setURL = function (url) { opts.url = url; }

	$.fn.getLastFile = function () { return last_file; }
	$.fn.clearLastFile = function () { last_file = null; }

	$.fn.dropzone = function(options) {
		// Extend our default options with those provided.
		opts = $.extend( {}, $.fn.dropzone.defaults, options);

		var id = this.attr("id");
		var dropzone = document.getElementById(id);

		log("adding dnd-file-upload functionalities to element with id: " + id);

		// hack for safari on windows: due to not supported drop/dragenter/dragover events we have to create a invisible <input type="file" /> tag instead
		if ($.client.browser == "Safari" && $.client.os == "Windows") {
			var fileInput = $("<input>");
			fileInput.attr( {
				type : "file"
			});
			fileInput.bind("change", change);
			fileInput.css( {
				'opacity' : '0',
				'width' : '100%',
				'height' : '100%'
			});
			fileInput.attr("multiple", "multiple");
			fileInput.click(function() {
				return false;
			});
			this.append(fileInput);
		} else {
			dropzone.addEventListener("drop", drop, true);
			var jQueryDropzone = $("#" + id);
			jQueryDropzone.bind("dragenter", dragenter);
			jQueryDropzone.bind("dragover", dragover);
		}

		return this;
	};

	$.fn.dropzone.defaults = {
		url : "",
		method : "POST",
		numConcurrentUploads : 3,
		printLogs : false,
		// update upload speed every second
		uploadRateRefreshTime : 1000
	};

	// invoked when new files are dropped
	$.fn.dropzone.newFilesDropped = function() {
	};

	// invoked when the upload for given file has been started
	$.fn.dropzone.uploadStarted = function(fileIndex, file) {
	};

	// invoked when the upload for given file has been finished
	$.fn.dropzone.uploadFinished = function(fileIndex, file, time) {
	};

        $.fn.dropzone.uploadFinishedResponse = function (xhr) {
	};

	// invoked when the progress for given file has changed
	$.fn.dropzone.fileUploadProgressUpdated = function(fileIndex, file,
			newProgress) {
	};

	// invoked when the upload speed of given file has changed
	$.fn.dropzone.fileUploadSpeedUpdated = function(fileIndex, file,
			KBperSecond) {
	};

	function dragenter(event) {
		event.stopPropagation();
		event.preventDefault();
		return false;
	}

	function dragover(event) {
		event.stopPropagation();
		event.preventDefault();
		return false;
	}

	function drop(event) {
		var dt = event.dataTransfer;
		var files = dt.files;

		event.preventDefault();
		uploadFiles(files);

		return false;
	}

	function log(logMsg) {
		if (opts.printLogs) {
			// console && console.log(logMsg);
		}
	}

	$.fn.startXHRAll = function (file, index) {
		var xhr = new XMLHttpRequest();
		var upload = xhr.upload;
		upload.fileIndex = index;
		upload.fileObj = file 
		upload.downloadStartTime = new Date().getTime();
		upload.currentStart = upload.downloadStartTime;
		upload.currentProgress = 0;
		upload.startData = 0;
		xhr.open(opts.method, opts.url);
		xhr.setRequestHeader("Cache-Control", "no-cache");
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
		xhr.setRequestHeader("X-File-Name", file.fileName);
		xhr.setRequestHeader("X-File-Size", file.fileSize);
		xhr.setRequestHeader("X-File-Type", file.type);
		xhr.setRequestHeader("Content-Type", "multipart/form-data");
		xhr.addEventListener('load', load2, false);
		xhr.send(file);
		return xhr;

	}

	$.fn.startXHRSlice = function(file, index, start, end) {
		var slice;
		if (file.slice) {
			slice = file.slice(start, end)
		} else {
			slice = file.getAsBinary().slice(start, end);
		}
		var xhr = new XMLHttpRequest();
		var upload = xhr.upload;
		upload.fileIndex = index;
		upload.fileObj = slice
		upload.downloadStartTime = new Date().getTime();
		upload.currentStart = upload.downloadStartTime;
		upload.currentProgress = 0;
		upload.startData = 0;
		xhr.open(opts.method, opts.url);
		xhr.setRequestHeader("Cache-Control", "no-cache");
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
		xhr.setRequestHeader("X-File-Name", file.fileName);
		xhr.setRequestHeader("X-File-Size", file.fileSize);
		xhr.setRequestHeader("X-Slice-Size", (end-start));
		xhr.setRequestHeader("X-Slice-Start", start);
		xhr.setRequestHeader("X-Slice-End", end);
		xhr.setRequestHeader("X-File-Type", file.type);
		xhr.setRequestHeader("Content-Type", "multipart/form-data");
		xhr.addEventListener('load', load2, false);
		if (!file.slice) {
			xhr.sendAsBinary(slice);
		} else {
			xhr.send(slice);
		}
		return xhr;
	}

	function uploadFiles(files) {
		$.fn.dropzone.newFilesDropped();
		var index = 0;
		for ( var i = 0; i < files.length; i++) {
			var file = files[i];

			// create a new xhr object
			last_file = file
			$.fn.startXHRSlice(file, index++, 0, 100)
			$.fn.dropzone.uploadStarted(i, file);
		}
	}

	function load(event) {
		var now = new Date().getTime();
		var timeDiff = now - this.downloadStartTime;
		$.fn.dropzone.uploadFinished(this.fileIndex, this.fileObj, timeDiff, event);
		log("finished loading of file " + this.fileIndex);
	}
	function load2(event) {
		$.fn.dropzone.uploadFinishedResponse(event.target)
	}

	function progress(event) {
		if (event.lengthComputable) {
			var percentage = Math.round((event.loaded * 100) / event.total);
			if (this.currentProgress != percentage) {

				// log(this.fileIndex + " --> " + percentage + "%");

				this.currentProgress = percentage;
				$.fn.dropzone.fileUploadProgressUpdated(this.fileIndex, this.fileObj, this.currentProgress);

				var elapsed = new Date().getTime();
				var diffTime = elapsed - this.currentStart;
				if (diffTime >= opts.uploadRateRefreshTime) {
					var diffData = event.loaded - this.startData;
					var speed = diffData / diffTime; // in KB/sec

					$.fn.dropzone.fileUploadSpeedUpdated(this.fileIndex, this.fileObj, speed);

					this.startData = event.loaded;
					this.currentStart = elapsed;
				}
			}
		}
	}

	// invoked when the input field has changed and new files have been dropped
	// or selected
	function change(event) {
		event.preventDefault();

		// get all files ...
		var files = this.files;

		// ... and upload them
		uploadFiles(files);
	}

})(jQuery);
