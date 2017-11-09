document.addEventListener('DOMContentLoaded', function() {
  window.addEventListener("message", (event) => {
      if (event.source !== window || !event.data){
          return;
      }
      if(event.data.action === 'verifying'){
		  showVerifyingDownload(event.data.fileName);
      }
      else if(event.data.action === 'verification-failed'){
		  showVerificationResult('failed');
      }
      else if(event.data.action === 'verification-failed-again'){
		  showVerificationResult('failed-again');
      }
      else if(event.data.action === 'verification-success'){
		  showVerificationResult('successful');
      }
      else if (event.data.action === 'progress'){
        showVerificationProgress(event.data.percentage);
      }
  });
  function showFloatingToggleableLinks() {
    var links = document.getElementsByClassName('floating-toggleable-link');
    for (let i = 0; i < links.length; i++) {
      links[i].style.display = 'block';
    }
  }
  showFloatingToggleableLinks();

  function opaque(elm) {
    elm.style.opacity = '1.0';
    var siblings = elm.querySelectorAll('a');
    for (let i = 0; i < siblings.length; i++) {
      siblings[i].style.pointerEvents = 'auto';
    }
  }

  function transparent(elm) {
    elm.style.opacity = '0.3';
    var siblings = elm.querySelectorAll('a');
    for (let i = 0; i < siblings.length; i++) {
      siblings[i].style.pointerEvents = 'none';
    }
  }

  function toggleOpacity(elm, mode) {
    for(var i = 0; i < elm.length; i++) {
      if(mode == 'opaque') {
        opaque(elm[i]);
      } else {
        transparent(elm[i]);
      }
    }
  }

  function hide(elm) {
    elm.style.display = 'none';
  }

  function show(elm) {
    elm.style.display = 'initial';
    if(elm.classList.contains('block')) {
      elm.style.display = 'block';
    }
    if(elm.classList.contains('inline-block')) {
      elm.style.display = 'inline-block';
    }
  }

  function toggleDisplay(elm, mode) {
    for(var i = 0; i < elm.length; i++) {
      if(mode == 'hide') {
        hide(elm[i]);
      } else {
        show(elm[i]);
      }
    }
  }

  function detectBrowser() {
    // XXX: Fix these minimum versions
    minVersion = {
      'firefox': 38,
      'chrome': 44,
      'torbrowser': 5
    };
    document.getElementById('min-version-firefox').textContent = minVersion.firefox.toString();
    document.getElementById('min-version-chrome').textContent = minVersion.chrome.toString();
    document.getElementById('min-version-tor-browser').textContent = minVersion.torbrowser.toString();

    version = navigator.userAgent.match(/\b(Chrome|Firefox)\/(\d+)/);
    version = version && parseInt(version[2]) || 0;
    overrideVersion = location.search.match(/\bversion=(\w+)/);
    if (overrideVersion) {
      version = overrideVersion[1];
    }

    overrideBrowser = location.search.match(/\bbrowser=(\w+)/);
    if (overrideBrowser) {
      browser = overrideBrowser[1];
    } else if (window.InstallTrigger) {
      browser = 'Firefox';
    } else if (/\bChrom/.test(navigator.userAgent) && /\bGoogle Inc\./.test(navigator.vendor)) {
      browser = 'Chrome';
    }

    if (browser === 'Firefox' || browser === 'Chrome') {
      document.getElementById('detected-browser').textContent = browser + ' ' + version.toString();
    } else {
      // Don't bother display version number for unsupported browsers as it's probably more error prone.
      document.getElementById('detected-browser').textContent = browser;
    }

    toggleDisplay(document.getElementsByClassName('no-js'), 'hide');
    if (browser === 'Firefox') {
      if (version >= minVersion.firefox) {
        // Supported Firefox
        toggleDisplay(document.getElementsByClassName('supported-browser'), 'show');
        toggleDisplay(document.getElementsByClassName('chrome'), 'hide');
        toggleDisplay(document.getElementsByClassName('firefox'), 'show');
      } else {
        // Outdated Firefox
        toggleDisplay(document.getElementsByClassName('outdated-browser'), 'show');
      }
    } else if (browser === 'Chrome') {
      if (version >= minVersion.chrome) {
        // Supported Chrome
        toggleDisplay(document.getElementsByClassName('supported-browser'), 'show');
        toggleDisplay(document.getElementsByClassName('firefox'), 'hide');
        toggleDisplay(document.getElementsByClassName('chrome'), 'show');
      } else {
        // Outdated Chrome
        toggleDisplay(document.getElementsByClassName('outdated-browser'), 'show');
      }
    } else {
      toggleDisplay(document.getElementsByClassName('unsupported-browser'), 'show');
    }
  }

  function toggleContinueLink(method, state) {
    if(method == 'direct') {
      hide(document.getElementById('skip-download-direct'));
      hide(document.getElementById('skip-verification-direct'));
      hide(document.getElementById('next-direct'));
      show(document.getElementById(state));
    }
    if(method == 'bittorrent') {
      hide(document.getElementById('skip-download-bittorrent'));
      hide(document.getElementById('next-bittorrent'));
      show(document.getElementById(state));
    }
  }

  function resetVerificationResult(result) {
    hide(document.getElementById('verifying-download'));
    hide(document.getElementById('verification-successful'));
    hide(document.getElementById('verification-failed'));
    hide(document.getElementById('verification-failed-again'));
    toggleContinueLink('direct', 'skip-verification-direct');
  }

  function showVerifyDownload() {
    hide(document.getElementById('install-extension'));
    hide(document.getElementById('update-extension'));
    show(document.getElementById('verification'));
  }

  function showVerifyingDownload(filename) {
    hide(document.getElementById('verify-download-wrapper'));
    document.getElementById("filename").innerHTML = filename;
    show(document.getElementById('verifying-download'));
  }

  function showVerificationProgress(percentage) {
    document.getElementById('progress-bar').style.width = percentage + '%';
    document.getElementById('progress-bar').setAttribute('aria-valuenow', percentage.toString());
  }

  function showVerificationResult(result) {
    hide(document.getElementById('verify-download-wrapper'));
    resetVerificationResult();
    if(result === 'successful') {
      show(document.getElementById('verification-successful'));
      opaque(document.getElementById('step-continue-direct'));
      toggleContinueLink('direct', 'next-direct');
    }
    else if(result === 'failed') {
      show(document.getElementById('verification-failed'));
    }
    else if(result === 'failed-again') {
      show(document.getElementById('verification-failed-again'));
    }
  }

  function toggleDirectBitTorrent(method) {
    transparent(document.getElementById('step-verify-direct'));
    transparent(document.getElementById('step-continue-direct'));
    transparent(document.getElementById('continue-link-direct'));
    transparent(document.getElementById('step-verify-bittorrent'));
    transparent(document.getElementById('step-continue-bittorrent'));
    transparent(document.getElementById('continue-link-bittorrent'));
    if(method == 'direct') {
      opaque(document.getElementById('step-verify-direct'));
      opaque(document.getElementById('continue-link-direct'));
      show(document.getElementById('verify-download-wrapper'));
    }
    if(method == 'bittorrent') {
      opaque(document.getElementById('step-verify-bittorrent'));
      opaque(document.getElementById('step-continue-bittorrent'));
      opaque(document.getElementById('continue-link-bittorrent'));
      toggleContinueLink('bittorrent', 'next-bittorrent');
    }
  }

  detectBrowser();
  toggleDirectBitTorrent('none');
  toggleContinueLink('direct', 'skip-download-direct');
  toggleContinueLink('bittorrent', 'skip-download-bittorrent');
  opaque(document.getElementById('continue-link-direct'));
  opaque(document.getElementById('continue-link-bittorrent'));

  // Display "Verify with your browser" when ISO image is clicked
  document.getElementById('download-iso').onclick = function() {
    toggleDirectBitTorrent('direct');
    resetVerificationResult();
  }

  // Display "Verify with BitTorrent" when Torrent file is clicked
  document.getElementById('download-torrent').onclick = function() {
    toggleDirectBitTorrent('bittorrent');
  }

});
