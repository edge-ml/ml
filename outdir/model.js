
var Module = (() => {
  var _scriptDir = typeof document !== 'undefined' && document.currentScript ? document.currentScript.src : undefined;
  if (typeof __filename !== 'undefined') _scriptDir = _scriptDir || __filename;
  return (
function(moduleArg = {}) {

// include: shell.js
// The Module object: Our interface to the outside world. We import
// and export values on it. There are various ways Module can be used:
// 1. Not defined. We create it here
// 2. A function parameter, function(Module) { ..generated code.. }
// 3. pre-run appended it, var Module = {}; ..generated code..
// 4. External script tag defines var Module.
// We need to check if Module already exists (e.g. case 3 above).
// Substitution will be replaced with actual code on later stage of the build,
// this way Closure Compiler will not mangle it (e.g. case 4. above).
// Note that if you want to run closure, and also to use Module
// after the generated code, you will need to define   var Module = {};
// before the code. Then that object will be used in the code, and you
// can continue to use Module afterwards as well.
var Module = moduleArg;

// Set up the promise that indicates the Module is initialized
var readyPromiseResolve, readyPromiseReject;
Module['ready'] = new Promise((resolve, reject) => {
  readyPromiseResolve = resolve;
  readyPromiseReject = reject;
});
["_main","_memory","___indirect_function_table","_fflush","onRuntimeInitialized"].forEach((prop) => {
  if (!Object.getOwnPropertyDescriptor(Module['ready'], prop)) {
    Object.defineProperty(Module['ready'], prop, {
      get: () => abort('You are getting ' + prop + ' on the Promise object, instead of the instance. Use .then() to get called back with the instance, see the MODULARIZE docs in src/settings.js'),
      set: () => abort('You are setting ' + prop + ' on the Promise object, instead of the instance. Use .then() to get called back with the instance, see the MODULARIZE docs in src/settings.js'),
    });
  }
});

// --pre-jses are emitted after the Module integration code, so that they can
// refer to Module (if they choose; they can also define Module)


// Sometimes an existing Module object exists with properties
// meant to overwrite the default module functionality. Here
// we collect those properties and reapply _after_ we configure
// the current environment's defaults to avoid having to be so
// defensive during initialization.
var moduleOverrides = Object.assign({}, Module);

var arguments_ = [];
var thisProgram = './this.program';
var quit_ = (status, toThrow) => {
  throw toThrow;
};

// Determine the runtime environment we are in. You can customize this by
// setting the ENVIRONMENT setting at compile time (see settings.js).

// Attempt to auto-detect the environment
var ENVIRONMENT_IS_WEB = typeof window == 'object';
var ENVIRONMENT_IS_WORKER = typeof importScripts == 'function';
// N.b. Electron.js environment is simultaneously a NODE-environment, but
// also a web environment.
var ENVIRONMENT_IS_NODE = typeof process == 'object' && typeof process.versions == 'object' && typeof process.versions.node == 'string';
var ENVIRONMENT_IS_SHELL = !ENVIRONMENT_IS_WEB && !ENVIRONMENT_IS_NODE && !ENVIRONMENT_IS_WORKER;

if (Module['ENVIRONMENT']) {
  throw new Error('Module.ENVIRONMENT has been deprecated. To force the environment, use the ENVIRONMENT compile-time option (for example, -sENVIRONMENT=web or -sENVIRONMENT=node)');
}

// `/` should be present at the end if `scriptDirectory` is not empty
var scriptDirectory = '';
function locateFile(path) {
  if (Module['locateFile']) {
    return Module['locateFile'](path, scriptDirectory);
  }
  return scriptDirectory + path;
}

// Hooks that are implemented differently in different runtime environments.
var read_,
    readAsync,
    readBinary;

if (ENVIRONMENT_IS_NODE) {
  if (typeof process == 'undefined' || !process.release || process.release.name !== 'node') throw new Error('not compiled for this environment (did you build to HTML and try to run it not on the web, or set ENVIRONMENT to something - like node - and run it someplace else - like on the web?)');

  var nodeVersion = process.versions.node;
  var numericVersion = nodeVersion.split('.').slice(0, 3);
  numericVersion = (numericVersion[0] * 10000) + (numericVersion[1] * 100) + (numericVersion[2].split('-')[0] * 1);
  var minVersion = 160000;
  if (numericVersion < 160000) {
    throw new Error('This emscripten-generated code requires node v16.0.0 (detected v' + nodeVersion + ')');
  }

  // `require()` is no-op in an ESM module, use `createRequire()` to construct
  // the require()` function.  This is only necessary for multi-environment
  // builds, `-sENVIRONMENT=node` emits a static import declaration instead.
  // TODO: Swap all `require()`'s with `import()`'s?
  // These modules will usually be used on Node.js. Load them eagerly to avoid
  // the complexity of lazy-loading.
  var fs = require('fs');
  var nodePath = require('path');

  if (ENVIRONMENT_IS_WORKER) {
    scriptDirectory = nodePath.dirname(scriptDirectory) + '/';
  } else {
    scriptDirectory = __dirname + '/';
  }

// include: node_shell_read.js
read_ = (filename, binary) => {
  // We need to re-wrap `file://` strings to URLs. Normalizing isn't
  // necessary in that case, the path should already be absolute.
  filename = isFileURI(filename) ? new URL(filename) : nodePath.normalize(filename);
  return fs.readFileSync(filename, binary ? undefined : 'utf8');
};

readBinary = (filename) => {
  var ret = read_(filename, true);
  if (!ret.buffer) {
    ret = new Uint8Array(ret);
  }
  assert(ret.buffer);
  return ret;
};

readAsync = (filename, onload, onerror, binary = true) => {
  // See the comment in the `read_` function.
  filename = isFileURI(filename) ? new URL(filename) : nodePath.normalize(filename);
  fs.readFile(filename, binary ? undefined : 'utf8', (err, data) => {
    if (err) onerror(err);
    else onload(binary ? data.buffer : data);
  });
};
// end include: node_shell_read.js
  if (!Module['thisProgram'] && process.argv.length > 1) {
    thisProgram = process.argv[1].replace(/\\/g, '/');
  }

  arguments_ = process.argv.slice(2);

  // MODULARIZE will export the module in the proper place outside, we don't need to export here

  quit_ = (status, toThrow) => {
    process.exitCode = status;
    throw toThrow;
  };

  Module['inspect'] = () => '[Emscripten Module object]';

} else
if (ENVIRONMENT_IS_SHELL) {

  if ((typeof process == 'object' && typeof require === 'function') || typeof window == 'object' || typeof importScripts == 'function') throw new Error('not compiled for this environment (did you build to HTML and try to run it not on the web, or set ENVIRONMENT to something - like node - and run it someplace else - like on the web?)');

  if (typeof read != 'undefined') {
    read_ = read;
  }

  readBinary = (f) => {
    if (typeof readbuffer == 'function') {
      return new Uint8Array(readbuffer(f));
    }
    let data = read(f, 'binary');
    assert(typeof data == 'object');
    return data;
  };

  readAsync = (f, onload, onerror) => {
    setTimeout(() => onload(readBinary(f)));
  };

  if (typeof clearTimeout == 'undefined') {
    globalThis.clearTimeout = (id) => {};
  }

  if (typeof setTimeout == 'undefined') {
    // spidermonkey lacks setTimeout but we use it above in readAsync.
    globalThis.setTimeout = (f) => (typeof f == 'function') ? f() : abort();
  }

  if (typeof scriptArgs != 'undefined') {
    arguments_ = scriptArgs;
  } else if (typeof arguments != 'undefined') {
    arguments_ = arguments;
  }

  if (typeof quit == 'function') {
    quit_ = (status, toThrow) => {
      // Unlike node which has process.exitCode, d8 has no such mechanism. So we
      // have no way to set the exit code and then let the program exit with
      // that code when it naturally stops running (say, when all setTimeouts
      // have completed). For that reason, we must call `quit` - the only way to
      // set the exit code - but quit also halts immediately.  To increase
      // consistency with node (and the web) we schedule the actual quit call
      // using a setTimeout to give the current stack and any exception handlers
      // a chance to run.  This enables features such as addOnPostRun (which
      // expected to be able to run code after main returns).
      setTimeout(() => {
        if (!(toThrow instanceof ExitStatus)) {
          let toLog = toThrow;
          if (toThrow && typeof toThrow == 'object' && toThrow.stack) {
            toLog = [toThrow, toThrow.stack];
          }
          err(`exiting due to exception: ${toLog}`);
        }
        quit(status);
      });
      throw toThrow;
    };
  }

  if (typeof print != 'undefined') {
    // Prefer to use print/printErr where they exist, as they usually work better.
    if (typeof console == 'undefined') console = /** @type{!Console} */({});
    console.log = /** @type{!function(this:Console, ...*): undefined} */ (print);
    console.warn = console.error = /** @type{!function(this:Console, ...*): undefined} */ (typeof printErr != 'undefined' ? printErr : print);
  }

} else

// Note that this includes Node.js workers when relevant (pthreads is enabled).
// Node.js workers are detected as a combination of ENVIRONMENT_IS_WORKER and
// ENVIRONMENT_IS_NODE.
if (ENVIRONMENT_IS_WEB || ENVIRONMENT_IS_WORKER) {
  if (ENVIRONMENT_IS_WORKER) { // Check worker, not web, since window could be polyfilled
    scriptDirectory = self.location.href;
  } else if (typeof document != 'undefined' && document.currentScript) { // web
    scriptDirectory = document.currentScript.src;
  }
  // When MODULARIZE, this JS may be executed later, after document.currentScript
  // is gone, so we saved it, and we use it here instead of any other info.
  if (_scriptDir) {
    scriptDirectory = _scriptDir;
  }
  // blob urls look like blob:http://site.com/etc/etc and we cannot infer anything from them.
  // otherwise, slice off the final part of the url to find the script directory.
  // if scriptDirectory does not contain a slash, lastIndexOf will return -1,
  // and scriptDirectory will correctly be replaced with an empty string.
  // If scriptDirectory contains a query (starting with ?) or a fragment (starting with #),
  // they are removed because they could contain a slash.
  if (scriptDirectory.indexOf('blob:') !== 0) {
    scriptDirectory = scriptDirectory.substr(0, scriptDirectory.replace(/[?#].*/, "").lastIndexOf('/')+1);
  } else {
    scriptDirectory = '';
  }

  if (!(typeof window == 'object' || typeof importScripts == 'function')) throw new Error('not compiled for this environment (did you build to HTML and try to run it not on the web, or set ENVIRONMENT to something - like node - and run it someplace else - like on the web?)');

  // Differentiate the Web Worker from the Node Worker case, as reading must
  // be done differently.
  {
// include: web_or_worker_shell_read.js
read_ = (url) => {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, false);
    xhr.send(null);
    return xhr.responseText;
  }

  if (ENVIRONMENT_IS_WORKER) {
    readBinary = (url) => {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', url, false);
      xhr.responseType = 'arraybuffer';
      xhr.send(null);
      return new Uint8Array(/** @type{!ArrayBuffer} */(xhr.response));
    };
  }

  readAsync = (url, onload, onerror) => {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'arraybuffer';
    xhr.onload = () => {
      if (xhr.status == 200 || (xhr.status == 0 && xhr.response)) { // file URLs can return 0
        onload(xhr.response);
        return;
      }
      onerror();
    };
    xhr.onerror = onerror;
    xhr.send(null);
  }

// end include: web_or_worker_shell_read.js
  }
} else
{
  throw new Error('environment detection error');
}

var out = Module['print'] || console.log.bind(console);
var err = Module['printErr'] || console.error.bind(console);

// Merge back in the overrides
Object.assign(Module, moduleOverrides);
// Free the object hierarchy contained in the overrides, this lets the GC
// reclaim data used e.g. in memoryInitializerRequest, which is a large typed array.
moduleOverrides = null;
checkIncomingModuleAPI();

// Emit code to handle expected values on the Module object. This applies Module.x
// to the proper local x. This has two benefits: first, we only emit it if it is
// expected to arrive, and second, by using a local everywhere else that can be
// minified.

if (Module['arguments']) arguments_ = Module['arguments'];legacyModuleProp('arguments', 'arguments_');

if (Module['thisProgram']) thisProgram = Module['thisProgram'];legacyModuleProp('thisProgram', 'thisProgram');

if (Module['quit']) quit_ = Module['quit'];legacyModuleProp('quit', 'quit_');

// perform assertions in shell.js after we set up out() and err(), as otherwise if an assertion fails it cannot print the message
// Assertions on removed incoming Module JS APIs.
assert(typeof Module['memoryInitializerPrefixURL'] == 'undefined', 'Module.memoryInitializerPrefixURL option was removed, use Module.locateFile instead');
assert(typeof Module['pthreadMainPrefixURL'] == 'undefined', 'Module.pthreadMainPrefixURL option was removed, use Module.locateFile instead');
assert(typeof Module['cdInitializerPrefixURL'] == 'undefined', 'Module.cdInitializerPrefixURL option was removed, use Module.locateFile instead');
assert(typeof Module['filePackagePrefixURL'] == 'undefined', 'Module.filePackagePrefixURL option was removed, use Module.locateFile instead');
assert(typeof Module['read'] == 'undefined', 'Module.read option was removed (modify read_ in JS)');
assert(typeof Module['readAsync'] == 'undefined', 'Module.readAsync option was removed (modify readAsync in JS)');
assert(typeof Module['readBinary'] == 'undefined', 'Module.readBinary option was removed (modify readBinary in JS)');
assert(typeof Module['setWindowTitle'] == 'undefined', 'Module.setWindowTitle option was removed (modify emscripten_set_window_title in JS)');
assert(typeof Module['TOTAL_MEMORY'] == 'undefined', 'Module.TOTAL_MEMORY has been renamed Module.INITIAL_MEMORY');
legacyModuleProp('asm', 'wasmExports');
legacyModuleProp('read', 'read_');
legacyModuleProp('readAsync', 'readAsync');
legacyModuleProp('readBinary', 'readBinary');
legacyModuleProp('setWindowTitle', 'setWindowTitle');
var IDBFS = 'IDBFS is no longer included by default; build with -lidbfs.js';
var PROXYFS = 'PROXYFS is no longer included by default; build with -lproxyfs.js';
var WORKERFS = 'WORKERFS is no longer included by default; build with -lworkerfs.js';
var FETCHFS = 'FETCHFS is no longer included by default; build with -lfetchfs.js';
var ICASEFS = 'ICASEFS is no longer included by default; build with -licasefs.js';
var JSFILEFS = 'JSFILEFS is no longer included by default; build with -ljsfilefs.js';
var OPFS = 'OPFS is no longer included by default; build with -lopfs.js';

var NODEFS = 'NODEFS is no longer included by default; build with -lnodefs.js';

assert(!ENVIRONMENT_IS_SHELL, "shell environment detected but not enabled at build time.  Add 'shell' to `-sENVIRONMENT` to enable.");


// end include: shell.js
// include: preamble.js
// === Preamble library stuff ===

// Documentation for the public APIs defined in this file must be updated in:
//    site/source/docs/api_reference/preamble.js.rst
// A prebuilt local version of the documentation is available at:
//    site/build/text/docs/api_reference/preamble.js.txt
// You can also build docs locally as HTML or other formats in site/
// An online HTML version (which may be of a different version of Emscripten)
//    is up at http://kripken.github.io/emscripten-site/docs/api_reference/preamble.js.html

var wasmBinary; 
if (Module['wasmBinary']) wasmBinary = Module['wasmBinary'];legacyModuleProp('wasmBinary', 'wasmBinary');

if (typeof WebAssembly != 'object') {
  abort('no native wasm support detected');
}

// include: base64Utils.js
// Converts a string of base64 into a byte array (Uint8Array).
function intArrayFromBase64(s) {
  if (typeof ENVIRONMENT_IS_NODE != 'undefined' && ENVIRONMENT_IS_NODE) {
    var buf = Buffer.from(s, 'base64');
    return new Uint8Array(buf.buffer, buf.byteOffset, buf.length);
  }

  var decoded = atob(s);
  var bytes = new Uint8Array(decoded.length);
  for (var i = 0 ; i < decoded.length ; ++i) {
    bytes[i] = decoded.charCodeAt(i);
  }
  return bytes;
}

// If filename is a base64 data URI, parses and returns data (Buffer on node,
// Uint8Array otherwise). If filename is not a base64 data URI, returns undefined.
function tryParseAsDataURI(filename) {
  if (!isDataURI(filename)) {
    return;
  }

  return intArrayFromBase64(filename.slice(dataURIPrefix.length));
}
// end include: base64Utils.js
// Wasm globals

var wasmMemory;

//========================================
// Runtime essentials
//========================================

// whether we are quitting the application. no code should run after this.
// set in exit() and abort()
var ABORT = false;

// set by exit() and abort().  Passed to 'onExit' handler.
// NOTE: This is also used as the process return code code in shell environments
// but only when noExitRuntime is false.
var EXITSTATUS;

// In STRICT mode, we only define assert() when ASSERTIONS is set.  i.e. we
// don't define it at all in release modes.  This matches the behaviour of
// MINIMAL_RUNTIME.
// TODO(sbc): Make this the default even without STRICT enabled.
/** @type {function(*, string=)} */
function assert(condition, text) {
  if (!condition) {
    abort('Assertion failed' + (text ? ': ' + text : ''));
  }
}

// We used to include malloc/free by default in the past. Show a helpful error in
// builds with assertions.

// Memory management

var HEAP,
/** @type {!Int8Array} */
  HEAP8,
/** @type {!Uint8Array} */
  HEAPU8,
/** @type {!Int16Array} */
  HEAP16,
/** @type {!Uint16Array} */
  HEAPU16,
/** @type {!Int32Array} */
  HEAP32,
/** @type {!Uint32Array} */
  HEAPU32,
/** @type {!Float32Array} */
  HEAPF32,
/** @type {!Float64Array} */
  HEAPF64;

function updateMemoryViews() {
  var b = wasmMemory.buffer;
  Module['HEAP8'] = HEAP8 = new Int8Array(b);
  Module['HEAP16'] = HEAP16 = new Int16Array(b);
  Module['HEAPU8'] = HEAPU8 = new Uint8Array(b);
  Module['HEAPU16'] = HEAPU16 = new Uint16Array(b);
  Module['HEAP32'] = HEAP32 = new Int32Array(b);
  Module['HEAPU32'] = HEAPU32 = new Uint32Array(b);
  Module['HEAPF32'] = HEAPF32 = new Float32Array(b);
  Module['HEAPF64'] = HEAPF64 = new Float64Array(b);
}

assert(!Module['STACK_SIZE'], 'STACK_SIZE can no longer be set at runtime.  Use -sSTACK_SIZE at link time')

assert(typeof Int32Array != 'undefined' && typeof Float64Array !== 'undefined' && Int32Array.prototype.subarray != undefined && Int32Array.prototype.set != undefined,
       'JS engine does not provide full typed array support');

// If memory is defined in wasm, the user can't provide it, or set INITIAL_MEMORY
assert(!Module['wasmMemory'], 'Use of `wasmMemory` detected.  Use -sIMPORTED_MEMORY to define wasmMemory externally');
assert(!Module['INITIAL_MEMORY'], 'Detected runtime INITIAL_MEMORY setting.  Use -sIMPORTED_MEMORY to define wasmMemory dynamically');

// include: runtime_stack_check.js
// Initializes the stack cookie. Called at the startup of main and at the startup of each thread in pthreads mode.
function writeStackCookie() {
  var max = _emscripten_stack_get_end();
  assert((max & 3) == 0);
  // If the stack ends at address zero we write our cookies 4 bytes into the
  // stack.  This prevents interference with SAFE_HEAP and ASAN which also
  // monitor writes to address zero.
  if (max == 0) {
    max += 4;
  }
  // The stack grow downwards towards _emscripten_stack_get_end.
  // We write cookies to the final two words in the stack and detect if they are
  // ever overwritten.
  HEAPU32[((max)>>2)] = 0x02135467;
  HEAPU32[(((max)+(4))>>2)] = 0x89BACDFE;
  // Also test the global address 0 for integrity.
  HEAPU32[((0)>>2)] = 1668509029;
}

function checkStackCookie() {
  if (ABORT) return;
  var max = _emscripten_stack_get_end();
  // See writeStackCookie().
  if (max == 0) {
    max += 4;
  }
  var cookie1 = HEAPU32[((max)>>2)];
  var cookie2 = HEAPU32[(((max)+(4))>>2)];
  if (cookie1 != 0x02135467 || cookie2 != 0x89BACDFE) {
    abort(`Stack overflow! Stack cookie has been overwritten at ${ptrToString(max)}, expected hex dwords 0x89BACDFE and 0x2135467, but received ${ptrToString(cookie2)} ${ptrToString(cookie1)}`);
  }
  // Also test the global address 0 for integrity.
  if (HEAPU32[((0)>>2)] != 0x63736d65 /* 'emsc' */) {
    abort('Runtime error: The application has corrupted its heap memory area (address zero)!');
  }
}
// end include: runtime_stack_check.js
// include: runtime_assertions.js
// Endianness check
(function() {
  var h16 = new Int16Array(1);
  var h8 = new Int8Array(h16.buffer);
  h16[0] = 0x6373;
  if (h8[0] !== 0x73 || h8[1] !== 0x63) throw 'Runtime error: expected the system to be little-endian! (Run with -sSUPPORT_BIG_ENDIAN to bypass)';
})();

// end include: runtime_assertions.js
var __ATPRERUN__  = []; // functions called before the runtime is initialized
var __ATINIT__    = []; // functions called during startup
var __ATEXIT__    = []; // functions called during shutdown
var __ATPOSTRUN__ = []; // functions called after the main() is called

var runtimeInitialized = false;

function preRun() {
  if (Module['preRun']) {
    if (typeof Module['preRun'] == 'function') Module['preRun'] = [Module['preRun']];
    while (Module['preRun'].length) {
      addOnPreRun(Module['preRun'].shift());
    }
  }
  callRuntimeCallbacks(__ATPRERUN__);
}

function initRuntime() {
  assert(!runtimeInitialized);
  runtimeInitialized = true;

  checkStackCookie();

  
  callRuntimeCallbacks(__ATINIT__);
}

function postRun() {
  checkStackCookie();

  if (Module['postRun']) {
    if (typeof Module['postRun'] == 'function') Module['postRun'] = [Module['postRun']];
    while (Module['postRun'].length) {
      addOnPostRun(Module['postRun'].shift());
    }
  }

  callRuntimeCallbacks(__ATPOSTRUN__);
}

function addOnPreRun(cb) {
  __ATPRERUN__.unshift(cb);
}

function addOnInit(cb) {
  __ATINIT__.unshift(cb);
}

function addOnExit(cb) {
}

function addOnPostRun(cb) {
  __ATPOSTRUN__.unshift(cb);
}

// include: runtime_math.js
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/imul

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/fround

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/clz32

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/trunc

assert(Math.imul, 'This browser does not support Math.imul(), build with LEGACY_VM_SUPPORT or POLYFILL_OLD_MATH_FUNCTIONS to add in a polyfill');
assert(Math.fround, 'This browser does not support Math.fround(), build with LEGACY_VM_SUPPORT or POLYFILL_OLD_MATH_FUNCTIONS to add in a polyfill');
assert(Math.clz32, 'This browser does not support Math.clz32(), build with LEGACY_VM_SUPPORT or POLYFILL_OLD_MATH_FUNCTIONS to add in a polyfill');
assert(Math.trunc, 'This browser does not support Math.trunc(), build with LEGACY_VM_SUPPORT or POLYFILL_OLD_MATH_FUNCTIONS to add in a polyfill');
// end include: runtime_math.js
// A counter of dependencies for calling run(). If we need to
// do asynchronous work before running, increment this and
// decrement it. Incrementing must happen in a place like
// Module.preRun (used by emcc to add file preloading).
// Note that you can add dependencies in preRun, even though
// it happens right before run - run will be postponed until
// the dependencies are met.
var runDependencies = 0;
var runDependencyWatcher = null;
var dependenciesFulfilled = null; // overridden to take different actions when all run dependencies are fulfilled
var runDependencyTracking = {};

function getUniqueRunDependency(id) {
  var orig = id;
  while (1) {
    if (!runDependencyTracking[id]) return id;
    id = orig + Math.random();
  }
}

function addRunDependency(id) {
  runDependencies++;

  if (Module['monitorRunDependencies']) {
    Module['monitorRunDependencies'](runDependencies);
  }

  if (id) {
    assert(!runDependencyTracking[id]);
    runDependencyTracking[id] = 1;
    if (runDependencyWatcher === null && typeof setInterval != 'undefined') {
      // Check for missing dependencies every few seconds
      runDependencyWatcher = setInterval(() => {
        if (ABORT) {
          clearInterval(runDependencyWatcher);
          runDependencyWatcher = null;
          return;
        }
        var shown = false;
        for (var dep in runDependencyTracking) {
          if (!shown) {
            shown = true;
            err('still waiting on run dependencies:');
          }
          err(`dependency: ${dep}`);
        }
        if (shown) {
          err('(end of list)');
        }
      }, 10000);
    }
  } else {
    err('warning: run dependency added without ID');
  }
}

function removeRunDependency(id) {
  runDependencies--;

  if (Module['monitorRunDependencies']) {
    Module['monitorRunDependencies'](runDependencies);
  }

  if (id) {
    assert(runDependencyTracking[id]);
    delete runDependencyTracking[id];
  } else {
    err('warning: run dependency removed without ID');
  }
  if (runDependencies == 0) {
    if (runDependencyWatcher !== null) {
      clearInterval(runDependencyWatcher);
      runDependencyWatcher = null;
    }
    if (dependenciesFulfilled) {
      var callback = dependenciesFulfilled;
      dependenciesFulfilled = null;
      callback(); // can add another dependenciesFulfilled
    }
  }
}

/** @param {string|number=} what */
function abort(what) {
  if (Module['onAbort']) {
    Module['onAbort'](what);
  }

  what = 'Aborted(' + what + ')';
  // TODO(sbc): Should we remove printing and leave it up to whoever
  // catches the exception?
  err(what);

  ABORT = true;
  EXITSTATUS = 1;

  // Use a wasm runtime error, because a JS error might be seen as a foreign
  // exception, which means we'd run destructors on it. We need the error to
  // simply make the program stop.
  // FIXME This approach does not work in Wasm EH because it currently does not assume
  // all RuntimeErrors are from traps; it decides whether a RuntimeError is from
  // a trap or not based on a hidden field within the object. So at the moment
  // we don't have a way of throwing a wasm trap from JS. TODO Make a JS API that
  // allows this in the wasm spec.

  // Suppress closure compiler warning here. Closure compiler's builtin extern
  // defintion for WebAssembly.RuntimeError claims it takes no arguments even
  // though it can.
  // TODO(https://github.com/google/closure-compiler/pull/3913): Remove if/when upstream closure gets fixed.
  /** @suppress {checkTypes} */
  var e = new WebAssembly.RuntimeError(what);

  readyPromiseReject(e);
  // Throw the error whether or not MODULARIZE is set because abort is used
  // in code paths apart from instantiation where an exception is expected
  // to be thrown when abort is called.
  throw e;
}

// include: memoryprofiler.js
// end include: memoryprofiler.js
// show errors on likely calls to FS when it was not included
var FS = {
  error() {
    abort('Filesystem support (FS) was not included. The problem is that you are using files from JS, but files were not used from C/C++, so filesystem support was not auto-included. You can force-include filesystem support with -sFORCE_FILESYSTEM');
  },
  init() { FS.error() },
  createDataFile() { FS.error() },
  createPreloadedFile() { FS.error() },
  createLazyFile() { FS.error() },
  open() { FS.error() },
  mkdev() { FS.error() },
  registerDevice() { FS.error() },
  analyzePath() { FS.error() },

  ErrnoError() { FS.error() },
};
Module['FS_createDataFile'] = FS.createDataFile;
Module['FS_createPreloadedFile'] = FS.createPreloadedFile;

// include: URIUtils.js
// Prefix of data URIs emitted by SINGLE_FILE and related options.
var dataURIPrefix = 'data:application/octet-stream;base64,';

/**
 * Indicates whether filename is a base64 data URI.
 * @noinline
 */
var isDataURI = (filename) => filename.startsWith(dataURIPrefix);

/**
 * Indicates whether filename is delivered via file protocol (as opposed to http/https)
 * @noinline
 */
var isFileURI = (filename) => filename.startsWith('file://');
// end include: URIUtils.js
function createExportWrapper(name) {
  return function() {
    assert(runtimeInitialized, `native function \`${name}\` called before runtime initialization`);
    var f = wasmExports[name];
    assert(f, `exported native function \`${name}\` not found`);
    return f.apply(null, arguments);
  };
}

// include: runtime_exceptions.js
// end include: runtime_exceptions.js
var wasmBinaryFile;
  wasmBinaryFile = 'data:application/octet-stream;base64,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KAIkIXtBASF8IHsgfGohfSAGIH02AiQMAQtBFCF+IAYgfmohfyB/IYABIIABEBgaIAYoAlQhgQEgBiCBATYCECAGKAJQIYIBQdwAIYMBIAYggwFqIYQBIIQBIYUBIIUBEBchhgFBECGHASAGIIcBaiGIASCIASGJASCJARCgASGKASCKARAXIYsBIIIBIIYBIIsBEHIhjAFBASGNASCMASCNAXEhjgECQCCOAQ0AA0BBFCGPASAGII8BaiGQASCQASGRAUEQIZIBIAYgkgFqIZMBIJMBIZQBIJEBIJQBEDMhlQFBASGWASCVASCWAXEhlwECQCCXAUUNAAwGCyAGKAJQIZgBQdwAIZkBIAYgmQFqIZoBIJoBIZsBIJsBEBchnAFBFCGdASAGIJ0BaiGeASCeASGfASCfARAXIaABIJgBIJwBIKABEHIhoQFBASGiASChASCiAXEhowECQAJAIKMBRQ0AQRQhpAEgBiCkAWohpQEgpQEhpgFBECGnASAGIKcBaiGoASCoASGpASCmASCpARChASAGKAIkIaoBQQEhqwEgqgEgqwFqIawBIAYgrAE2AiRBFCGtASAGIK0BaiGuASCuASGvASCvARAYGgwBC0EUIbABIAYgsAFqIbEBILEBIbIBILIBEBgaDAELCwtBFCGzASAGILMBaiG0ASC0ASG1AUEQIbYBIAYgtgFqIbcBILcBIbgBILUBILgBEDMhuQFBASG6ASC5ASC6AXEhuwECQCC7AUUNAAwECwNAAkADQCAGKAJQIbwBQdwAIb0BIAYgvQFqIb4BIL4BIb8BIL8BEBchwAFBFCHBASAGIMEBaiHCASDCASHDASDDARAXIcQBILwBIMABIMQBEHIhxQFBfyHGASDFASDGAXMhxwFBASHIASDHASDIAXEhyQEgyQFFDQFBFCHKASAGIMoBaiHLASDLASHMASDMARAYGgwACwALAkADQCAGKAJQIc0BQdwAIc4BIAYgzgFqIc8BIM8BIdABINABEBch0QFBECHSASAGINIBaiHTASDTASHUASDUARCgASHVASDVARAXIdYBIM0BINEBINYBEHIh1wFBASHYASDXASDYAXEh2QEg2QFFDQEMAAsAC0EUIdoBIAYg2gFqIdsBINsBIdwBQRAh3QEgBiDdAWoh3gEg3gEh3wEg3AEg3wEQpQEh4AFBASHh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KAIQNgIQIAIgASgCFDYCFCACIAEoAhg2AhggAiABKAIcNgIcIAIgASgCIDYCICACIAEoAiQ2AiQgAiABKAIoNgIoIAIgASgCLDYCLCACIAEoAjA2AjAgAiABKAI0NgI0IAIgASgCODYCOCACIAEoAjw2AjwgAUHAAGohASACQcAAaiICIAVNDQALCyACIARPDQEDQCACIAEoAgA2AgAgAUEEaiEBIAJBBGoiAiAESQ0ADAILAAsCQCADQQRPDQAgACECDAELAkAgA0F8aiIEIABPDQAgACECDAELIAAhAgNAIAIgAS0AADoAACACIAEtAAE6AAEgAiABLQACOgACIAIgAS0AAzoAAyABQQRqIQEgAkEEaiICIARNDQALCwJAIAIgA08NAANAIAIgAS0AADoAACABQQFqIQEgAkEBaiICIANHDQALCyAAC/cCAQJ/AkAgACABRg0AAkAgASAAIAJqIgNrQQAgAkEBdGtLDQAgACABIAIQzwIPCyABIABzQQNxIQQCQAJAAkAgACABTw0AAkAgBEUNACAAIQMMAwsCQCAAQQNxDQAgACEDDAILIAAhAwNAIAJFDQQgAyABLQAAOgAAIAFBAWohASACQX9qIQIgA0EBaiIDQQNxRQ0CDAALAAsCQCAEDQACQCADQQNxRQ0AA0AgAkUNBSAAIAJBf2oiAmoiAyABIAJqLQAAOgAAIANBA3ENAAsLIAJBA00NAANAIAAgAkF8aiICaiABIAJqKAIANgIAIAJBA0sNAAsLIAJFDQIDQCAAIAJBf2oiAmogASACai0AADoAACACDQAMAwsACyACQQNNDQADQCADIAEoAgA2AgAgAUEEaiEBIANBBGohAyACQXxqIgJBA0sNAAsLIAJFDQADQCADIAEtAAA6AAAgA0EBaiEDIAFBAWohASACQX9qIgINAAsLIAALJAECfwJAIAAQ0gJBAWoiARDXAiICDQBBAA8LIAIgACABEM8CC4UBAQN/IAAhAQJAAkAgAEEDcUUNAAJAIAAtAAANACAAIABrDwsgACEBA0AgAUEBaiIBQQNxRQ0BIAEtAAANAAwCCwALA0AgASICQQRqIQEgAigCACIDQX9zIANB//37d2pxQYCBgoR4cUUNAAsDQCACIgFBAWohAiABLQAADQALCyABIABrCwcAPwBBEHQLBgBBqJkEC1QBAn9BACgCuJcEIgEgAEEHakF4cSICaiEAAkACQCACRQ0AIAAgAU0NAQsCQCAAENMCTQ0AIAAQC0UNAQtBACAANgK4lwQgAQ8LENQCQTA2AgBBfwvyAgIDfwF+AkAgAkUNACAAIAE6AAAgACACaiIDQX9qIAE6AAAgAkEDSQ0AIAAgAToAAiAAIAE6AAEgA0F9aiABOgAAIANBfmogAToAACACQQdJDQAgACABOgADIANBfGogAToAACACQQlJDQAgAEEAIABrQQNxIgRqIgMgAUH/AXFBgYKECGwiATYCACADIAIgBGtBfHEiBGoiAkF8aiABNgIAIARBCUkNACADIAE2AgggAyABNgIEIAJBeGogATYCACACQXRqIAE2AgAgBEEZSQ0AIAMgATYCGCADIAE2AhQgAyABNgIQIAMgATYCDCACQXBqIAE2AgAgAkFsaiABNgIAIAJBaGogATYCACACQWRqIAE2AgAgBCADQQRxQRhyIgVrIgJBIEkNACABrUKBgICAEH4hBiADIAVqIQEDQCABIAY3AxggASAGNwMQIAEgBjcDCCABIAY3AwAgAUEgaiEBIAJBYGoiAkEfSw0ACwsgAAvcIgELfyMAQRBrIgEkAAJAAkACQAJAAkACQAJAAkACQAJAIABB9AFLDQACQEEAKAKsmQQiAkEQIABBC2pBeHEgAEELSRsiA0EDdiIEdiIAQQNxRQ0AAkACQCAAQX9zQQFxIARqIgVBA3QiBEHUmQRqIgAgBEHcmQRqKAIAIgQoAggiA0cNAEEAIAJBfiAFd3E2AqyZBAwBCyADIAA2AgwgACADNgIICyAEQQhqIQAgBCAFQQN0IgVBA3I2AgQgBCAFaiIEIAQoAgRBAXI2AgQMCgsgA0EAKAK0mQQiBk0NAQJAIABFDQACQAJAIAAgBHRBAiAEdCIAQQAgAGtycWgiBEEDdCIAQdSZBGoiBSAAQdyZBGooAgAiACgCCCIHRw0AQQAgAkF+IAR3cSICNgKsmQQMAQsgByAFNgIMIAUgBzYCCAsgACADQQNyNgIEIAAgA2oiByAEQQN0IgQgA2siBUEBcjYCBCAAIARqIAU2AgACQCAGRQ0AIAZBeHFB1JkEaiEDQQAoAsCZBCEEAkACQCACQQEgBkEDdnQiCHENAEEAIAIgCHI2AqyZBCADIQgMAQsgAygCCCEICyADIAQ2AgggCCAENgIMIAQgAzYCDCAEIAg2AggLIABBCGohAEEAIAc2AsCZBEEAIAU2ArSZBAwKC0EAKAKwmQQiCUUNASAJaEECdEHcmwRqKAIAIgcoAgRBeHEgA2shBCAHIQUCQANAAkAgBSgCECIADQAgBUEUaigCACIARQ0CCyAAKAIEQXhxIANrIgUgBCAFIARJIgUbIQQgACAHIAUbIQcgACEFDAALAAsgBygCGCEKAkAgBygCDCIIIAdGDQAgBygCCCIAQQAoAryZBEkaIAAgCDYCDCAIIAA2AggMCQsCQCAHQRRqIgUoAgAiAA0AIAcoAhAiAEUNAyAHQRBqIQULA0AgBSELIAAiCEEUaiIFKAIAIgANACAIQRBqIQUgCCgCECIADQALIAtBADYCAAwIC0F/IQMgAEG/f0sNACAAQQtqIgBBeHEhA0EAKAKwmQQiBkUNAEEAIQsCQCADQYACSQ0AQR8hCyADQf///wdLDQAgA0EmIABBCHZnIgBrdkEBcSAAQQF0a0E+aiELC0EAIANrIQQCQAJAAkACQCALQQJ0QdybBGooAgAiBQ0AQQAhAEEAIQgMAQtBACEAIANBAEEZIAtBAXZrIAtBH0YbdCEHQQAhCANAAkAgBSgCBEF4cSADayICIARPDQAgAiEEIAUhCCACDQBBACEEIAUhCCAFIQAMAwsgACAFQRRqKAIAIgIgAiAFIAdBHXZBBHFqQRBqKAIAIgVGGyAAIAIbIQAgB0EBdCEHIAUNAAsLAkAgACAIcg0AQQAhCEECIAt0IgBBACAAa3IgBnEiAEUNAyAAaEECdEHcmwRqKAIAIQALIABFDQELA0AgACgCBEF4cSADayICIARJIQcCQCAAKAIQIgUNACAAQRRqKAIAIQULIAIgBCAHGyEEIAAgCCAHGyEIIAUhACAFDQALCyAIRQ0AIARBACgCtJkEIANrTw0AIAgoAhghCwJAIAgoAgwiByAIRg0AIAgoAggiAEEAKAK8mQRJGiAAIAc2AgwgByAANgIIDAcLAkAgCEEUaiIFKAIAIgANACAIKAIQIgBFDQMgCEEQaiEFCwNAIAUhAiAAIgdBFGoiBSgCACIADQAgB0EQaiEFIAcoAhAiAA0ACyACQQA2AgAMBgsCQEEAKAK0mQQiACADSQ0AQQAoAsCZBCEEAkACQCAAIANrIgVBEEkNACAEIANqIgcgBUEBcjYCBCAEIABqIAU2AgAgBCADQQNyNgIEDAELIAQgAEEDcjYCBCAEIABqIgAgACgCBEEBcjYCBEEAIQdBACEFC0EAIAU2ArSZBEEAIAc2AsCZBCAEQQhqIQAMCAsCQEEAKAK4mQQiByADTQ0AQQAgByADayIENgK4mQRBAEEAKALEmQQiACADaiIFNgLEmQQgBSAEQQFyNgIEIAAgA0EDcjYCBCAAQQhqIQAMCAsCQAJAQQAoAoSdBEUNAEEAKAKMnQQhBAwBC0EAQn83ApCdBEEAQoCggICAgAQ3AoidBEEAIAFBDGpBcHFB2KrVqgVzNgKEnQRBAEEANgKYnQRBAEEANgLonARBgCAhBAtBACEAIAQgA0EvaiIGaiICQQAgBGsiC3EiCCADTQ0HQQAhAAJAQQAoAuScBCIERQ0AQQAoAtycBCIFIAhqIgogBU0NCCAKIARLDQgLAkACQEEALQDonARBBHENAAJAAkACQAJAAkBBACgCxJkEIgRFDQBB7JwEIQADQAJAIAAoAgAiBSAESw0AIAUgACgCBGogBEsNAwsgACgCCCIADQALC0EAENUCIgdBf0YNAyAIIQICQEEAKAKInQQiAEF/aiIEIAdxRQ0AIAggB2sgBCAHakEAIABrcWohAgsgAiADTQ0DAkBBACgC5JwEIgBFDQBBACgC3JwEIgQgAmoiBSAETQ0EIAUgAEsNBAsgAhDVAiIAIAdHDQEMBQsgAiAHayALcSICENUCIgcgACgCACAAKAIEakYNASAHIQALIABBf0YNAQJAIAIgA0EwakkNACAAIQcMBAsgBiACa0EAKAKMnQQiBGpBACAEa3EiBBDVAkF/Rg0BIAQgAmohAiAAIQcMAwsgB0F/Rw0CC0EAQQAoAuicBEEEcjYC6JwECyAIENUCIQdBABDVAiEAIAdBf0YNBSAAQX9GDQUgByAATw0FIAAgB2siAiADQShqTQ0FC0EAQQAoAtycBCACaiIANgLcnAQCQCAAQQAoAuCcBE0NAEEAIAA2AuCcBAsCQAJAQQAoAsSZBCIERQ0AQeycBCEAA0AgByAAKAIAIgUgACgCBCIIakYNAiAAKAIIIgANAAwFCwALAkACQEEAKAK8mQQiAEUNACAHIABPDQELQQAgBzYCvJkEC0EAIQBBACACNgLwnARBACAHNgLsnARBAEF/NgLMmQRBAEEAKAKEnQQ2AtCZBEEAQQA2AvicBANAIABBA3QiBEHcmQRqIARB1JkEaiIFNgIAIARB4JkEaiAFNgIAIABBAWoiAEEgRw0AC0EAIAJBWGoiAEF4IAdrQQdxIgRrIgU2AriZBEEAIAcgBGoiBDYCxJkEIAQgBUEBcjYCBCAHIABqQSg2AgRBAEEAKAKUnQQ2AsiZBAwECyAEIAdPDQIgBCAFSQ0CIAAoAgxBCHENAiAAIAggAmo2AgRBACAEQXggBGtBB3EiAGoiBTYCxJkEQQBBACgCuJkEIAJqIgcgAGsiADYCuJkEIAUgAEEBcjYCBCAEIAdqQSg2AgRBAEEAKAKUnQQ2AsiZBAwDC0EAIQgMBQtBACEHDAMLAkAgB0EAKAK8mQRPDQBBACAHNgK8mQQLIAcgAmohBUHsnAQhAAJAAkACQAJAA0AgACgCACAFRg0BIAAoAggiAA0ADAILAAsgAC0ADEEIcUUNAQtB7JwEIQACQANAAkAgACgCACIFIARLDQAgBSAAKAIEaiIFIARLDQILIAAoAgghAAwACwALQQAgAkFYaiIAQXggB2tBB3EiCGsiCzYCuJkEQQAgByAIaiIINgLEmQQgCCALQQFyNgIEIAcgAGpBKDYCBEEAQQAoApSdBDYCyJkEIAQgBUEnIAVrQQdxakFRaiIAIAAgBEEQakkbIghBGzYCBCAIQRBqQQApAvScBDcCACAIQQApAuycBDcCCEEAIAhBCGo2AvScBEEAIAI2AvCcBEEAIAc2AuycBEEAQQA2AvicBCAIQRhqIQADQCAAQQc2AgQgAEEIaiEHIABBBGohACAHIAVJDQALIAggBEYNAiAIIAgoAgRBfnE2AgQgBCAIIARrIgdBAXI2AgQgCCAHNgIAAkAgB0H/AUsNACAHQXhxQdSZBGohAAJAAkBBACgCrJkEIgVBASAHQQN2dCIHcQ0AQQAgBSAHcjYCrJkEIAAhBQwBCyAAKAIIIQULIAAgBDYCCCAFIAQ2AgwgBCAANgIMIAQgBTYCCAwDC0EfIQACQCAHQf///wdLDQAgB0EmIAdBCHZnIgBrdkEBcSAAQQF0a0E+aiEACyAEIAA2AhwgBEIANwIQIABBAnRB3JsEaiEFAkACQEEAKAKwmQQiCEEBIAB0IgJxDQBBACAIIAJyNgKwmQQgBSAENgIAIAQgBTYCGAwBCyAHQQBBGSAAQQF2ayAAQR9GG3QhACAFKAIAIQgDQCAIIgUoAgRBeHEgB0YNAyAAQR12IQggAEEBdCEAIAUgCEEEcWpBEGoiAigCACIIDQALIAIgBDYCACAEIAU2AhgLIAQgBDYCDCAEIAQ2AggMAgsgACAHNgIAIAAgACgCBCACajYCBCAHIAUgAxDYAiEADAULIAUoAggiACAENgIMIAUgBDYCCCAEQQA2AhggBCAFNgIMIAQgADYCCAtBACgCuJkEIgAgA00NAEEAIAAgA2siBDYCuJkEQQBBACgCxJkEIgAgA2oiBTYCxJkEIAUgBEEBcjYCBCAAIANBA3I2AgQgAEEIaiEADAMLENQCQTA2AgBBACEADAILAkAgC0UNAAJAAkAgCCAIKAIcIgVBAnRB3JsEaiIAKAIARw0AIAAgBzYCACAHDQFBACAGQX4gBXdxIgY2ArCZBAwCCyALQRBBFCALKAIQIAhGG2ogBzYCACAHRQ0BCyAHIAs2AhgCQCAIKAIQIgBFDQAgByAANgIQIAAgBzYCGAsgCEEUaigCACIARQ0AIAdBFGogADYCACAAIAc2AhgLAkACQCAEQQ9LDQAgCCAEIANqIgBBA3I2AgQgCCAAaiIAIAAoAgRBAXI2AgQMAQsgCCADQQNyNgIEIAggA2oiByAEQQFyNgIEIAcgBGogBDYCAAJAIARB/wFLDQAgBEF4cUHUmQRqIQACQAJAQQAoAqyZBCIFQQEgBEEDdnQiBHENAEEAIAUgBHI2AqyZBCAAIQQMAQsgACgCCCEECyAAIAc2AgggBCAHNgIMIAcgADYCDCAHIAQ2AggMAQtBHyEAAkAgBEH///8HSw0AIARBJiAEQQh2ZyIAa3ZBAXEgAEEBdGtBPmohAAsgByAANgIcIAdCADcCECAAQQJ0QdybBGohBQJAAkACQCAGQQEgAHQiA3ENAEEAIAYgA3I2ArCZBCAFIAc2AgAgByAFNgIYDAELIARBAEEZIABBAXZrIABBH0YbdCEAIAUoAgAhAwNAIAMiBSgCBEF4cSAERg0CIABBHXYhAyAAQQF0IQAgBSADQQRxakEQaiICKAIAIgMNAAsgAiAHNgIAIAcgBTYCGAsgByAHNgIMIAcgBzYCCAwBCyAFKAIIIgAgBzYCDCAFIAc2AgggB0EANgIYIAcgBTYCDCAHIAA2AggLIAhBCGohAAwBCwJAIApFDQACQAJAIAcgBygCHCIFQQJ0QdybBGoiACgCAEcNACAAIAg2AgAgCA0BQQAgCUF+IAV3cTYCsJkEDAILIApBEEEUIAooAhAgB0YbaiAINgIAIAhFDQELIAggCjYCGAJAIAcoAhAiAEUNACAIIAA2AhAgACAINgIYCyAHQRRqKAIAIgBFDQAgCEEUaiAANgIAIAAgCDYCGAsCQAJAIARBD0sNACAHIAQgA2oiAEEDcjYCBCAHIABqIgAgACgCBEEBcjYCBAwBCyAHIANBA3I2AgQgByADaiIFIARBAXI2AgQgBSAEaiAENgIAAkAgBkUNACAGQXhxQdSZBGohA0EAKALAmQQhAAJAAkBBASAGQQN2dCIIIAJxDQBBACAIIAJyNgKsmQQgAyEIDAELIAMoAgghCAsgAyAANgIIIAggADYCDCAAIAM2AgwgACAINgIIC0EAIAU2AsCZBEEAIAQ2ArSZBAsgB0EIaiEACyABQRBqJAAgAAuNCAEHfyAAQXggAGtBB3FqIgMgAkEDcjYCBCABQXggAWtBB3FqIgQgAyACaiIFayECAkACQCAEQQAoAsSZBEcNAEEAIAU2AsSZBEEAQQAoAriZBCACaiICNgK4mQQgBSACQQFyNgIEDAELAkAgBEEAKALAmQRHDQBBACAFNgLAmQRBAEEAKAK0mQQgAmoiAjYCtJkEIAUgAkEBcjYCBCAFIAJqIAI2AgAMAQsCQCAEKAIEIgBBA3FBAUcNACAAQXhxIQYCQAJAIABB/wFLDQAgBCgCCCIBIABBA3YiB0EDdEHUmQRqIghGGgJAIAQoAgwiACABRw0AQQBBACgCrJkEQX4gB3dxNgKsmQQMAgsgACAIRhogASAANgIMIAAgATYCCAwBCyAEKAIYIQkCQAJAIAQoAgwiCCAERg0AIAQoAggiAEEAKAK8mQRJGiAAIAg2AgwgCCAANgIIDAELAkACQCAEQRRqIgEoAgAiAA0AIAQoAhAiAEUNASAEQRBqIQELA0AgASEHIAAiCEEUaiIBKAIAIgANACAIQRBqIQEgCCgCECIADQALIAdBADYCAAwBC0EAIQgLIAlFDQACQAJAIAQgBCgCHCIBQQJ0QdybBGoiACgCAEcNACAAIAg2AgAgCA0BQQBBACgCsJkEQX4gAXdxNgKwmQQMAgsgCUEQQRQgCSgCECAERhtqIAg2AgAgCEUNAQsgCCAJNgIYAkAgBCgCECIARQ0AIAggADYCECAAIAg2AhgLIARBFGooAgAiAEUNACAIQRRqIAA2AgAgACAINgIYCyAGIAJqIQIgBCAGaiIEKAIEIQALIAQgAEF+cTYCBCAFIAJBAXI2AgQgBSACaiACNgIAAkAgAkH/AUsNACACQXhxQdSZBGohAAJAAkBBACgCrJkEIgFBASACQQN2dCICcQ0AQQAgASACcjYCrJkEIAAhAgwBCyAAKAIIIQILIAAgBTYCCCACIAU2AgwgBSAANgIMIAUgAjYCCAwBC0EfIQACQCACQf///wdLDQAgAkEmIAJBCHZnIgBrdkEBcSAAQQF0a0E+aiEACyAFIAA2AhwgBUIANwIQIABBAnRB3JsEaiEBAkACQAJAQQAoArCZBCIIQQEgAHQiBHENAEEAIAggBHI2ArCZBCABIAU2AgAgBSABNgIYDAELIAJBAEEZIABBAXZrIABBH0YbdCEAIAEoAgAhCANAIAgiASgCBEF4cSACRg0CIABBHXYhCCAAQQF0IQAgASAIQQRxakEQaiIEKAIAIggNAAsgBCAFNgIAIAUgATYCGAsgBSAFNgIMIAUgBTYCCAwBCyABKAIIIgIgBTYCDCABIAU2AgggBUEANgIYIAUgATYCDCAFIAI2AggLIANBCGoL2wwBB38CQCAARQ0AIABBeGoiASAAQXxqKAIAIgJBeHEiAGohAwJAIAJBAXENACACQQNxRQ0BIAEgASgCACICayIBQQAoAryZBCIESQ0BIAIgAGohAAJAAkACQCABQQAoAsCZBEYNAAJAIAJB/wFLDQAgASgCCCIEIAJBA3YiBUEDdEHUmQRqIgZGGgJAIAEoAgwiAiAERw0AQQBBACgCrJkEQX4gBXdxNgKsmQQMBQsgAiAGRhogBCACNgIMIAIgBDYCCAwECyABKAIYIQcCQCABKAIMIgYgAUYNACABKAIIIgIgBEkaIAIgBjYCDCAGIAI2AggMAwsCQCABQRRqIgQoAgAiAg0AIAEoAhAiAkUNAiABQRBqIQQLA0AgBCEFIAIiBkEUaiIEKAIAIgINACAGQRBqIQQgBigCECICDQALIAVBADYCAAwCCyADKAIEIgJBA3FBA0cNAkEAIAA2ArSZBCADIAJBfnE2AgQgASAAQQFyNgIEIAMgADYCAA8LQQAhBgsgB0UNAAJAAkAgASABKAIcIgRBAnRB3JsEaiICKAIARw0AIAIgBjYCACAGDQFBAEEAKAKwmQRBfiAEd3E2ArCZBAwCCyAHQRBBFCAHKAIQIAFGG2ogBjYCACAGRQ0BCyAGIAc2AhgCQCABKAIQIgJFDQAgBiACNgIQIAIgBjYCGAsgAUEUaigCACICRQ0AIAZBFGogAjYCACACIAY2AhgLIAEgA08NACADKAIEIgJBAXFFDQACQAJAAkACQAJAIAJBAnENAAJAIANBACgCxJkERw0AQQAgATYCxJkEQQBBACgCuJkEIABqIgA2AriZBCABIABBAXI2AgQgAUEAKALAmQRHDQZBAEEANgK0mQRBAEEANgLAmQQPCwJAIANBACgCwJkERw0AQQAgATYCwJkEQQBBACgCtJkEIABqIgA2ArSZBCABIABBAXI2AgQgASAAaiAANgIADwsgAkF4cSAAaiEAAkAgAkH/AUsNACADKAIIIgQgAkEDdiIFQQN0QdSZBGoiBkYaAkAgAygCDCICIARHDQBBAEEAKAKsmQRBfiAFd3E2AqyZBAwFCyACIAZGGiAEIAI2AgwgAiAENgIIDAQLIAMoAhghBwJAIAMoAgwiBiADRg0AIAMoAggiAkEAKAK8mQRJGiACIAY2AgwgBiACNgIIDAMLAkAgA0EUaiIEKAIAIgINACADKAIQIgJFDQIgA0EQaiEECwNAIAQhBSACIgZBFGoiBCgCACICDQAgBkEQaiEEIAYoAhAiAg0ACyAFQQA2AgAMAgsgAyACQX5xNgIEIAEgAEEBcjYCBCABIABqIAA2AgAMAwtBACEGCyAHRQ0AAkACQCADIAMoAhwiBEECdEHcmwRqIgIoAgBHDQAgAiAGNgIAIAYNAUEAQQAoArCZBEF+IAR3cTYCsJkEDAILIAdBEEEUIAcoAhAgA0YbaiAGNgIAIAZFDQELIAYgBzYCGAJAIAMoAhAiAkUNACAGIAI2AhAgAiAGNgIYCyADQRRqKAIAIgJFDQAgBkEUaiACNgIAIAIgBjYCGAsgASAAQQFyNgIEIAEgAGogADYCACABQQAoAsCZBEcNAEEAIAA2ArSZBA8LAkAgAEH/AUsNACAAQXhxQdSZBGohAgJAAkBBACgCrJkEIgRBASAAQQN2dCIAcQ0AQQAgBCAAcjYCrJkEIAIhAAwBCyACKAIIIQALIAIgATYCCCAAIAE2AgwgASACNgIMIAEgADYCCA8LQR8hAgJAIABB////B0sNACAAQSYgAEEIdmciAmt2QQFxIAJBAXRrQT5qIQILIAEgAjYCHCABQgA3AhAgAkECdEHcmwRqIQQCQAJAAkACQEEAKAKwmQQiBkEBIAJ0IgNxDQBBACAGIANyNgKwmQQgBCABNgIAIAEgBDYCGAwBCyAAQQBBGSACQQF2ayACQR9GG3QhAiAEKAIAIQYDQCAGIgQoAgRBeHEgAEYNAiACQR12IQYgAkEBdCECIAQgBkEEcWpBEGoiAygCACIGDQALIAMgATYCACABIAQ2AhgLIAEgATYCDCABIAE2AggMAQsgBCgCCCIAIAE2AgwgBCABNgIIIAFBADYCGCABIAQ2AgwgASAANgIIC0EAQQAoAsyZBEF/aiIBQX8gARs2AsyZBAsLpQMBBX9BECECAkACQCAAQRAgAEEQSxsiAyADQX9qcQ0AIAMhAAwBCwNAIAIiAEEBdCECIAAgA0kNAAsLAkBBQCAAayABSw0AENQCQTA2AgBBAA8LAkBBECABQQtqQXhxIAFBC0kbIgEgAGpBDGoQ1wIiAg0AQQAPCyACQXhqIQMCQAJAIABBf2ogAnENACADIQAMAQsgAkF8aiIEKAIAIgVBeHEgAiAAakF/akEAIABrcUF4aiICQQAgACACIANrQQ9LG2oiACADayICayEGAkAgBUEDcQ0AIAMoAgAhAyAAIAY2AgQgACADIAJqNgIADAELIAAgBiAAKAIEQQFxckECcjYCBCAAIAZqIgYgBigCBEEBcjYCBCAEIAIgBCgCAEEBcXJBAnI2AgAgAyACaiIGIAYoAgRBAXI2AgQgAyACENwCCwJAIAAoAgQiAkEDcUUNACACQXhxIgMgAUEQak0NACAAIAEgAkEBcXJBAnI2AgQgACABaiICIAMgAWsiAUEDcjYCBCAAIANqIgMgAygCBEEBcjYCBCACIAEQ3AILIABBCGoLdAECfwJAAkACQCABQQhHDQAgAhDXAiEBDAELQRwhAyABQQRJDQEgAUEDcQ0BIAFBAnYiBCAEQX9qcQ0BQTAhA0FAIAFrIAJJDQEgAUEQIAFBEEsbIAIQ2gIhAQsCQCABDQBBMA8LIAAgATYCAEEAIQMLIAMLlQwBBn8gACABaiECAkACQCAAKAIEIgNBAXENACADQQNxRQ0BIAAoAgAiAyABaiEBAkACQAJAAkAgACADayIAQQAoAsCZBEYNAAJAIANB/wFLDQAgACgCCCIEIANBA3YiBUEDdEHUmQRqIgZGGiAAKAIMIgMgBEcNAkEAQQAoAqyZBEF+IAV3cTYCrJkEDAULIAAoAhghBwJAIAAoAgwiBiAARg0AIAAoAggiA0EAKAK8mQRJGiADIAY2AgwgBiADNgIIDAQLAkAgAEEUaiIEKAIAIgMNACAAKAIQIgNFDQMgAEEQaiEECwNAIAQhBSADIgZBFGoiBCgCACIDDQAgBkEQaiEEIAYoAhAiAw0ACyAFQQA2AgAMAwsgAigCBCIDQQNxQQNHDQNBACABNgK0mQQgAiADQX5xNgIEIAAgAUEBcjYCBCACIAE2AgAPCyADIAZGGiAEIAM2AgwgAyAENgIIDAILQQAhBgsgB0UNAAJAAkAgACAAKAIcIgRBAnRB3JsEaiIDKAIARw0AIAMgBjYCACAGDQFBAEEAKAKwmQRBfiAEd3E2ArCZBAwCCyAHQRBBFCAHKAIQIABGG2ogBjYCACAGRQ0BCyAGIAc2AhgCQCAAKAIQIgNFDQAgBiADNgIQIAMgBjYCGAsgAEEUaigCACIDRQ0AIAZBFGogAzYCACADIAY2AhgLAkACQAJAAkACQCACKAIEIgNBAnENAAJAIAJBACgCxJkERw0AQQAgADYCxJkEQQBBACgCuJkEIAFqIgE2AriZBCAAIAFBAXI2AgQgAEEAKALAmQRHDQZBAEEANgK0mQRBAEEANgLAmQQPCwJAIAJBACgCwJkERw0AQQAgADYCwJkEQQBBACgCtJkEIAFqIgE2ArSZBCAAIAFBAXI2AgQgACABaiABNgIADwsgA0F4cSABaiEBAkAgA0H/AUsNACACKAIIIgQgA0EDdiIFQQN0QdSZBGoiBkYaAkAgAigCDCIDIARHDQBBAEEAKAKsmQRBfiAFd3E2AqyZBAwFCyADIAZGGiAEIAM2AgwgAyAENgIIDAQLIAIoAhghBwJAIAIoAgwiBiACRg0AIAIoAggiA0EAKAK8mQRJGiADIAY2AgwgBiADNgIIDAMLAkAgAkEUaiIEKAIAIgMNACACKAIQIgNFDQIgAkEQaiEECwNAIAQhBSADIgZBFGoiBCgCACIDDQAgBkEQaiEEIAYoAhAiAw0ACyAFQQA2AgAMAgsgAiADQX5xNgIEIAAgAUEBcjYCBCAAIAFqIAE2AgAMAwtBACEGCyAHRQ0AAkACQCACIAIoAhwiBEECdEHcmwRqIgMoAgBHDQAgAyAGNgIAIAYNAUEAQQAoArCZBEF+IAR3cTYCsJkEDAILIAdBEEEUIAcoAhAgAkYbaiAGNgIAIAZFDQELIAYgBzYCGAJAIAIoAhAiA0UNACAGIAM2AhAgAyAGNgIYCyACQRRqKAIAIgNFDQAgBkEUaiADNgIAIAMgBjYCGAsgACABQQFyNgIEIAAgAWogATYCACAAQQAoAsCZBEcNAEEAIAE2ArSZBA8LAkAgAUH/AUsNACABQXhxQdSZBGohAwJAAkBBACgCrJkEIgRBASABQQN2dCIBcQ0AQQAgBCABcjYCrJkEIAMhAQwBCyADKAIIIQELIAMgADYCCCABIAA2AgwgACADNgIMIAAgATYCCA8LQR8hAwJAIAFB////B0sNACABQSYgAUEIdmciA2t2QQFxIANBAXRrQT5qIQMLIAAgAzYCHCAAQgA3AhAgA0ECdEHcmwRqIQQCQAJAAkBBACgCsJkEIgZBASADdCICcQ0AQQAgBiACcjYCsJkEIAQgADYCACAAIAQ2AhgMAQsgAUEAQRkgA0EBdmsgA0EfRht0IQMgBCgCACEGA0AgBiIEKAIEQXhxIAFGDQIgA0EddiEGIANBAXQhAyAEIAZBBHFqQRBqIgIoAgAiBg0ACyACIAA2AgAgACAENgIYCyAAIAA2AgwgACAANgIIDwsgBCgCCCIBIAA2AgwgBCAANgIIIABBADYCGCAAIAQ2AgwgACABNgIICwtFAQJ/IwBBEGsiAiQAQQAhAwJAIABBA3ENACABIABwDQAgAkEMaiAAIAEQ2wIhAEEAIAIoAgwgABshAwsgAkEQaiQAIAMLNgEBfyAAQQEgAEEBSxshAQJAA0AgARDXAiIADQECQBCxAyIARQ0AIAARCAAMAQsLEAwACyAACwcAIAAQ2QILPwECfyABQQQgAUEESxshAiAAQQEgAEEBSxshAAJAA0AgAiAAEOECIgMNARCxAyIBRQ0BIAERCAAMAAsACyADCyEBAX8gACAAIAFqQX9qQQAgAGtxIgIgASACIAFLGxDdAgsHACAAEOMCCwcAIAAQ2QILEAAgAEHIlQRBCGo2AgAgAAs8AQJ/IAEQ0gIiAkENahDeAiIDQQA2AgggAyACNgIEIAMgAjYCACAAIAMQ5gIgASACQQFqEM8CNgIAIAALBwAgAEEMagsgACAAEOQCIgBBuJYEQQhqNgIAIABBBGogARDlAhogAAsEAEEBCwQAQQELAgALAgALAgALDQBBnJ0EEOsCQaCdBAsJAEGcnQQQ7AILBAAgAAsMACAAKAI8EO8CEA0LFgACQCAADQBBAA8LENQCIAA2AgBBfwvlAgEHfyMAQSBrIgMkACADIAAoAhwiBDYCECAAKAIUIQUgAyACNgIcIAMgATYCGCADIAUgBGsiATYCFCABIAJqIQYgA0EQaiEEQQIhBwJAAkACQAJAAkAgACgCPCADQRBqQQIgA0EMahAOEPECRQ0AIAQhBQwBCwNAIAYgAygCDCIBRg0CAkAgAUF/Sg0AIAQhBQwECyAEIAEgBCgCBCIISyIJQQN0aiIFIAUoAgAgASAIQQAgCRtrIghqNgIAIARBDEEEIAkbaiIEIAQoAgAgCGs2AgAgBiABayEGIAUhBCAAKAI8IAUgByAJayIHIANBDGoQDhDxAkUNAAsLIAZBf0cNAQsgACAAKAIsIgE2AhwgACABNgIUIAAgASAAKAIwajYCECACIQEMAQtBACEBIABBADYCHCAAQgA3AxAgACAAKAIAQSByNgIAIAdBAkYNACACIAUoAgRrIQELIANBIGokACABCzkBAX8jAEEQayIDJAAgACABIAJB/wFxIANBCGoQ6QMQ8QIhAiADKQMIIQEgA0EQaiQAQn8gASACGwsOACAAKAI8IAEgAhDzAgsEACAACxEAIAAQlgEoAghB/////wdxCwoAIAAQigMoAgALCgAgABCKAxCLAwsMACAAIAEtAAA6AAALGQAgABCHAxCIAyIAIAAQiQNBAXZLdkFwagstAQF/QQohAQJAIABBC0kNACAAQQFqEI4DIgAgAEF/aiIAIABBC0YbIQELIAELBwAgABCNAwsZACABIAIQjAMhASAAIAI2AgQgACABNgIACwIACw4AIAEgAiAAEI8DGiAACwsAIAAgASACEJIDCwwAIAAQigMgATYCAAs6AQF/IAAQigMiAiACKAIIQYCAgIB4cSABQf////8HcXI2AgggABCKAyIAIAAoAghBgICAgHhyNgIICwwAIAAQigMgATYCBAsKAEG5gQQQugEACwcAIABBC0kLLQEBfyAAEIoDIgIgAi0AC0GAAXEgAXI6AAsgABCKAyIAIAAtAAtB/wBxOgALCwcAIAAQlAMLBQAQiQMLBQAQlQMLBwAgABCXAwsEACAACxoAAkAgABCIAyABTw0AEMYBAAsgAUEBEMcBCwcAIAAQmAMLCgAgAEEPakFwcQsOACAAIAAgAWogAhCZAwsmACAAEJEDAkAgABCTAUUNACAAEPwCIAAQ9wIgABD2AhCAAwsgAAsCAAsLACABIAJBARDqAQujAQECfyMAQRBrIgMkAAJAIAAQ+gIgAkkNAAJAAkAgAhCFA0UNACAAIAIQhgMgABD4AiEEDAELIANBCGogABD8AiACEPsCQQFqEP0CIAMoAggiBCADKAIMEP4CIAAgBBCBAyAAIAMoAgwQggMgACACEIMDCyAEEPUCIAEgAhD/AhogA0EAOgAHIAQgAmogA0EHahD5AiADQRBqJAAPCyAAEIQDAAsHACAAEJYDCwQAQX8LBAAgAAsEACAACwQAIAALKwEBfyMAQRBrIgMkACADQQhqIAAgASACEJoDIAMoAgwhAiADQRBqJAAgAgsNACAAIAEgAiADEJsDCw0AIAAgASACIAMQnAMLaQEBfyMAQSBrIgQkACAEQRhqIAEgAhCdAyAEQRBqIARBDGogBCgCGCAEKAIcIAMQngMQnwMgBCABIAQoAhAQoAM2AgwgBCADIAQoAhQQoQM2AgggACAEQQxqIARBCGoQogMgBEEgaiQACwsAIAAgASACEKMDCwcAIAAQpQMLDQAgACACIAMgBBCkAwsJACAAIAEQpwMLCQAgACABEKgDCwwAIAAgASACEKYDGgs4AQF/IwBBEGsiAyQAIAMgARCpAzYCDCADIAIQqQM2AgggACADQQxqIANBCGoQqgMaIANBEGokAAtAAQF/IwBBEGsiBCQAIAQgAjYCDCAEIAMgASACIAFrIgIQ0AIgAmo2AgggACAEQQxqIARBCGoQrAMgBEEQaiQACwcAIAAQ9QILGAAgACABKAIANgIAIAAgAigCADYCBCAACwkAIAAgARCuAwsNACAAIAEgABD1AmtqCwcAIAAQqwMLGAAgACABKAIANgIAIAAgAigCADYCBCAACwcAIAAQkgELDAAgACABIAIQrQMaCxgAIAAgASgCADYCACAAIAIoAgA2AgQgAAsJACAAIAEQrwMLDQAgACABIAAQkgFragsHACAAKAIACwkAQbCdBBCwAwsPACAAQdAAahDXAkHQAGoLWQECfyABLQAAIQICQCAALQAAIgNFDQAgAyACQf8BcUcNAANAIAEtAAEhAiAALQABIgNFDQEgAUEBaiEBIABBAWohACADIAJB/wFxRg0ACwsgAyACQf8BcWsLBwAgABDaAwsCAAsCAAsKACAAELQDEN8CCwoAIAAQtAMQ3wILCgAgABC0AxDfAgsLACAAIAFBABC7AwswAAJAIAINACAAKAIEIAEoAgRGDwsCQCAAIAFHDQBBAQ8LIAAQvAMgARC8AxCzA0ULBwAgACgCBAutAQECfyMAQcAAayIDJABBASEEAkAgACABQQAQuwMNAEEAIQQgAUUNAEEAIQQgAUH8kARBrJEEQQAQvgMiAUUNACADQQxqQQBBNBDWAhogA0EBNgI4IANBfzYCFCADIAA2AhAgAyABNgIIIAEgA0EIaiACKAIAQQEgASgCACgCHBEHAAJAIAMoAiAiBEEBRw0AIAIgAygCGDYCAAsgBEEBRiEECyADQcAAaiQAIAQLzAIBA38jAEHAAGsiBCQAIAAoAgAiBUF8aigCACEGIAVBeGooAgAhBSAEQSBqQgA3AgAgBEEoakIANwIAIARBMGpCADcCACAEQTdqQgA3AAAgBEIANwIYIAQgAzYCFCAEIAE2AhAgBCAANgIMIAQgAjYCCCAAIAVqIQBBACEDAkACQCAGIAJBABC7A0UNACAEQQE2AjggBiAEQQhqIAAgAEEBQQAgBigCACgCFBEMACAAQQAgBCgCIEEBRhshAwwBCyAGIARBCGogAEEBQQAgBigCACgCGBEJAAJAAkAgBCgCLA4CAAECCyAEKAIcQQAgBCgCKEEBRhtBACAEKAIkQQFGG0EAIAQoAjBBAUYbIQMMAQsCQCAEKAIgQQFGDQAgBCgCMA0BIAQoAiRBAUcNASAEKAIoQQFHDQELIAQoAhghAwsgBEHAAGokACADC2ABAX8CQCABKAIQIgQNACABQQE2AiQgASADNgIYIAEgAjYCEA8LAkACQCAEIAJHDQAgASgCGEECRw0BIAEgAzYCGA8LIAFBAToANiABQQI2AhggASABKAIkQQFqNgIkCwsfAAJAIAAgASgCCEEAELsDRQ0AIAEgASACIAMQvwMLCzgAAkAgACABKAIIQQAQuwNFDQAgASABIAIgAxC/Aw8LIAAoAggiACABIAIgAyAAKAIAKAIcEQcAC58BACABQQE6ADUCQCABKAIEIANHDQAgAUEBOgA0AkACQCABKAIQIgMNACABQQE2AiQgASAENgIYIAEgAjYCECAEQQFHDQIgASgCMEEBRg0BDAILAkAgAyACRw0AAkAgASgCGCIDQQJHDQAgASAENgIYIAQhAwsgASgCMEEBRw0CIANBAUYNAQwCCyABIAEoAiRBAWo2AiQLIAFBAToANgsLIAACQCABKAIEIAJHDQAgASgCHEEBRg0AIAEgAzYCHAsLggIAAkAgACABKAIIIAQQuwNFDQAgASABIAIgAxDDAw8LAkACQCAAIAEoAgAgBBC7A0UNAAJAAkAgASgCECACRg0AIAEoAhQgAkcNAQsgA0EBRw0CIAFBATYCIA8LIAEgAzYCIAJAIAEoAixBBEYNACABQQA7ATQgACgCCCIAIAEgAiACQQEgBCAAKAIAKAIUEQwAAkAgAS0ANUUNACABQQM2AiwgAS0ANEUNAQwDCyABQQQ2AiwLIAEgAjYCFCABIAEoAihBAWo2AiggASgCJEEBRw0BIAEoAhhBAkcNASABQQE6ADYPCyAAKAIIIgAgASACIAMgBCAAKAIAKAIYEQkACwubAQACQCAAIAEoAgggBBC7A0UNACABIAEgAiADEMMDDwsCQCAAIAEoAgAgBBC7A0UNAAJAAkAgASgCECACRg0AIAEoAhQgAkcNAQsgA0EBRw0BIAFBATYCIA8LIAEgAjYCFCABIAM2AiAgASABKAIoQQFqNgIoAkAgASgCJEEBRw0AIAEoAhhBAkcNACABQQE6ADYLIAFBBDYCLAsLPgACQCAAIAEoAgggBRC7A0UNACABIAEgAiADIAQQwgMPCyAAKAIIIgAgASACIAMgBCAFIAAoAgAoAhQRDAALIQACQCAAIAEoAgggBRC7A0UNACABIAEgAiADIAQQwgMLCx4AAkAgAA0AQQAPCyAAQfyQBEGMkgRBABC+A0EARwsEACAACw0AIAAQyQMaIAAQ3wILBgBB1oAECxUAIAAQ5AIiAEGglQRBCGo2AgAgAAsNACAAEMkDGiAAEN8CCwYAQYSCBAsVACAAEMwDIgBBtJUEQQhqNgIAIAALDQAgABDJAxogABDfAgsGAEGJgQQLHAAgAEG4lgRBCGo2AgAgAEEEahDTAxogABDJAwsrAQF/AkAgABDoAkUNACAAKAIAENQDIgFBCGoQ1QNBf0oNACABEN8CCyAACwcAIABBdGoLFQEBfyAAIAAoAgBBf2oiATYCACABCw0AIAAQ0gMaIAAQ3wILCgAgAEEEahDYAwsHACAAKAIACw0AIAAQ0gMaIAAQ3wILBAAgAAsGACAAJAELBAAjAQsSAEGAgAQkA0EAQQ9qQXBxJAILBwAjACMCawsEACMDCwQAIwILwwIBA38CQCAADQBBACEBAkBBACgCpJ0ERQ0AQQAoAqSdBBDhAyEBCwJAQQAoAtCYBEUNAEEAKALQmAQQ4QMgAXIhAQsCQBDtAigCACIARQ0AA0BBACECAkAgACgCTEEASA0AIAAQ6QIhAgsCQCAAKAIUIAAoAhxGDQAgABDhAyABciEBCwJAIAJFDQAgABDqAgsgACgCOCIADQALCxDuAiABDwsCQAJAIAAoAkxBAE4NAEEBIQIMAQsgABDpAkUhAgsCQAJAAkAgACgCFCAAKAIcRg0AIABBAEEAIAAoAiQRBQAaIAAoAhQNAEF/IQEgAkUNAQwCCwJAIAAoAgQiASAAKAIIIgNGDQAgACABIANrrEEBIAAoAigRDQAaC0EAIQEgAEEANgIcIABCADcDECAAQgA3AgQgAg0BCyAAEOoCCyABCwQAIwALBgAgACQACxIBAn8jACAAa0FwcSIBJAAgAQsEACMACw0AIAEgAiADIAARDQALJQEBfiAAIAEgAq0gA61CIIaEIAQQ5gMhBSAFQiCIpxDbAyAFpwscACAAIAEgAiADpyADQiCIpyAEpyAEQiCIpxAPCxMAIAAgAacgAUIgiKcgAiADEBALC+EYAgBBgIAEC7QXdW5zaWduZWQgc2hvcnQAYWRkX2RhdGFwb2ludAB1bnNpZ25lZCBpbnQAcHJlZGljdABmbG9hdAB1aW50NjRfdAB2ZWN0b3IAdW5zaWduZWQgY2hhcgBzdGQ6OmV4Y2VwdGlvbgBib29sAGNsYXNzX3RvX2xhYmVsAGVtc2NyaXB0ZW46OnZhbABiYWRfYXJyYXlfbmV3X2xlbmd0aAB1bnNpZ25lZCBsb25nAHN0ZDo6d3N0cmluZwBiYXNpY19zdHJpbmcAc3RkOjpzdHJpbmcAc3RkOjp1MTZzdHJpbmcAc3RkOjp1MzJzdHJpbmcAZG91YmxlAG5vc2hha2UAdm9pZABzdGQ6OmJhZF9hbGxvYwBlbXNjcmlwdGVuOjptZW1vcnlfdmlldzxzaG9ydD4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8dW5zaWduZWQgc2hvcnQ+AGVtc2NyaXB0ZW46Om1lbW9yeV92aWV3PGludD4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8dW5zaWduZWQgaW50PgBlbXNjcmlwdGVuOjptZW1vcnlfdmlldzxmbG9hdD4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8dWludDhfdD4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8aW50OF90PgBlbXNjcmlwdGVuOjptZW1vcnlfdmlldzx1aW50MTZfdD4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8aW50MTZfdD4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8dWludDY0X3Q+AGVtc2NyaXB0ZW46Om1lbW9yeV92aWV3PGludDY0X3Q+AGVtc2NyaXB0ZW46Om1lbW9yeV92aWV3PHVpbnQzMl90PgBlbXNjcmlwdGVuOjptZW1vcnlfdmlldzxpbnQzMl90PgBlbXNjcmlwdGVuOjptZW1vcnlfdmlldzxjaGFyPgBlbXNjcmlwdGVuOjptZW1vcnlfdmlldzx1bnNpZ25lZCBjaGFyPgBzdGQ6OmJhc2ljX3N0cmluZzx1bnNpZ25lZCBjaGFyPgBlbXNjcmlwdGVuOjptZW1vcnlfdmlldzxzaWduZWQgY2hhcj4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8bG9uZz4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8dW5zaWduZWQgbG9uZz4AZW1zY3JpcHRlbjo6bWVtb3J5X3ZpZXc8ZG91YmxlPgAAAACARcXNzPzBzcz8wQAAAAAAAAAAzcz8wc3MzD3NzJzCzcxMPpqRNcXNzAbCc2jowW5b4j2OJUg8AACgwc3MTD4zM5DCZmZmQACAIsUAANDBAADQwbefXz6kV0M9mpkxwZqZEUEzM5fCmpnZQP9/90RmZp5BZmaeQblf1UFu2DFEAAAwQgAAMEJmZp5BzcycQmZm4kMAAJBAYOWQQPCFq0Fp2OVDZmZ+QQAAoEFmZoZAMzOQQgAom0WamUZCmplGQicfKELO0dxEzcycQs3MnEIAAKhBMzOXQsAJAQBpaQAAAAAAAAAAAABsCQEACAoBAAgKAQAICgEAdmlmZmYAAAAABQEAwAkBAE5TdDNfXzIxMmJhc2ljX3N0cmluZ0ljTlNfMTFjaGFyX3RyYWl0c0ljRUVOU185YWxsb2NhdG9ySWNFRUVFAAAkCgEAwAQBAGlpaQBOU3QzX18yMTJiYXNpY19zdHJpbmdJaE5TXzExY2hhcl90cmFpdHNJaEVFTlNfOWFsbG9jYXRvckloRUVFRQAAJAoBAAwFAQBOU3QzX18yMTJiYXNpY19zdHJpbmdJd05TXzExY2hhcl90cmFpdHNJd0VFTlNfOWFsbG9jYXRvckl3RUVFRQAAJAoBAFQFAQBOU3QzX18yMTJiYXNpY19zdHJpbmdJRHNOU18xMWNoYXJfdHJhaXRzSURzRUVOU185YWxsb2NhdG9ySURzRUVFRQAAACQKAQCcBQEATlN0M19fMjEyYmFzaWNfc3RyaW5nSURpTlNfMTFjaGFyX3RyYWl0c0lEaUVFTlNfOWFsbG9jYXRvcklEaUVFRUUAAAAkCgEA6AUBAE4xMGVtc2NyaXB0ZW4zdmFsRQAAJAoBADQGAQBOMTBlbXNjcmlwdGVuMTFtZW1vcnlfdmlld0ljRUUAACQKAQBQBgEATjEwZW1zY3JpcHRlbjExbWVtb3J5X3ZpZXdJYUVFAAAkCgEAeAYBAE4xMGVtc2NyaXB0ZW4xMW1lbW9yeV92aWV3SWhFRQAAJAoBAKAGAQBOMTBlbXNjcmlwdGVuMTFtZW1vcnlfdmlld0lzRUUAACQKAQDIBgEATjEwZW1zY3JpcHRlbjExbWVtb3J5X3ZpZXdJdEVFAAAkCgEA8AYBAE4xMGVtc2NyaXB0ZW4xMW1lbW9yeV92aWV3SWlFRQAAJAoBABgHAQBOMTBlbXNjcmlwdGVuMTFtZW1vcnlfdmlld0lqRUUAACQKAQBABwEATjEwZW1zY3JpcHRlbjExbWVtb3J5X3ZpZXdJbEVFAAAkCgEAaAcBAE4xMGVtc2NyaXB0ZW4xMW1lbW9yeV92aWV3SW1FRQAAJAoBAJAHAQBOMTBlbXNjcmlwdGVuMTFtZW1vcnlfdmlld0l4RUUAACQKAQC4BwEATjEwZW1zY3JpcHRlbjExbWVtb3J5X3ZpZXdJeUVFAAAkCgEA4AcBAE4xMGVtc2NyaXB0ZW4xMW1lbW9yeV92aWV3SWZFRQAAJAoBAAgIAQBOMTBlbXNjcmlwdGVuMTFtZW1vcnlfdmlld0lkRUUAACQKAQAwCAEATjEwX19jeHhhYml2MTE2X19zaGltX3R5cGVfaW5mb0UAAAAATAoBAFgIAQCsCwEATjEwX19jeHhhYml2MTE3X19jbGFzc190eXBlX2luZm9FAAAATAoBAIgIAQB8CAEATjEwX19jeHhhYml2MTE3X19wYmFzZV90eXBlX2luZm9FAAAATAoBALgIAQB8CAEATjEwX19jeHhhYml2MTE5X19wb2ludGVyX3R5cGVfaW5mb0UATAoBAOgIAQDcCAEAAAAAAFwJAQATAAAAFAAAABUAAAAWAAAAFwAAAE4xMF9fY3h4YWJpdjEyM19fZnVuZGFtZW50YWxfdHlwZV9pbmZvRQBMCgEANAkBAHwIAQB2AAAAIAkBAGgJAQBiAAAAIAkBAHQJAQBjAAAAIAkBAIAJAQBoAAAAIAkBAIwJAQBhAAAAIAkBAJgJAQBzAAAAIAkBAKQJAQB0AAAAIAkBALAJAQBpAAAAIAkBALwJAQBqAAAAIAkBAMgJAQBsAAAAIAkBANQJAQBtAAAAIAkBAOAJAQB4AAAAIAkBAOwJAQB5AAAAIAkBAPgJAQBmAAAAIAkBAAQKAQBkAAAAIAkBABAKAQAAAAAArAgBABMAAAAYAAAAFQAAABYAAAAZAAAAGgAAABsAAAAcAAAAAAAAAJQKAQATAAAAHQAAABUAAAAWAAAAGQAAAB4AAAAfAAAAIAAAAE4xMF9fY3h4YWJpdjEyMF9fc2lfY2xhc3NfdHlwZV9pbmZvRQAAAABMCgEAbAoBAKwIAQAAAAAABAsBAA4AAAAhAAAAIgAAAAAAAAAsCwEADgAAACMAAAAkAAAAAAAAAOwKAQAOAAAAJQAAACYAAABTdDlleGNlcHRpb24AAAAAJAoBANwKAQBTdDliYWRfYWxsb2MAAAAATAoBAPQKAQDsCgEAU3QyMGJhZF9hcnJheV9uZXdfbGVuZ3RoAAAAAEwKAQAQCwEABAsBAAAAAABcCwEADQAAACcAAAAoAAAAU3QxMWxvZ2ljX2Vycm9yAEwKAQBMCwEA7AoBAAAAAACQCwEADQAAACkAAAAoAAAAU3QxMmxlbmd0aF9lcnJvcgAAAABMCgEAfAsBAFwLAQBTdDl0eXBlX2luZm8AAAAAJAoBAJwLAQAAQbiXBAucAcAOAQAAAAAABQAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEQAAABIAAACwDgEAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAP//////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAsBAA==';
  if (!isDataURI(wasmBinaryFile)) {
    wasmBinaryFile = locateFile(wasmBinaryFile);
  }

function getBinarySync(file) {
  if (file == wasmBinaryFile && wasmBinary) {
    return new Uint8Array(wasmBinary);
  }
  var binary = tryParseAsDataURI(file);
  if (binary) {
    return binary;
  }
  if (readBinary) {
    return readBinary(file);
  }
  throw "both async and sync fetching of the wasm failed";
}

function getBinaryPromise(binaryFile) {

  // Otherwise, getBinarySync should be able to get it synchronously
  return Promise.resolve().then(() => getBinarySync(binaryFile));
}

function instantiateArrayBuffer(binaryFile, imports, receiver) {
  return getBinaryPromise(binaryFile).then((binary) => {
    return WebAssembly.instantiate(binary, imports);
  }).then((instance) => {
    return instance;
  }).then(receiver, (reason) => {
    err(`failed to asynchronously prepare wasm: ${reason}`);

    // Warn on some common problems.
    if (isFileURI(wasmBinaryFile)) {
      err(`warning: Loading from a file URI (${wasmBinaryFile}) is not supported in most browsers. See https://emscripten.org/docs/getting_started/FAQ.html#how-do-i-run-a-local-webserver-for-testing-why-does-my-program-stall-in-downloading-or-preparing`);
    }
    abort(reason);
  });
}

function instantiateAsync(binary, binaryFile, imports, callback) {
  return instantiateArrayBuffer(binaryFile, imports, callback);
}

// Create the wasm instance.
// Receives the wasm imports, returns the exports.
function createWasm() {
  // prepare imports
  var info = {
    'env': wasmImports,
    'wasi_snapshot_preview1': wasmImports,
  };
  // Load the wasm module and create an instance of using native support in the JS engine.
  // handle a generated wasm instance, receiving its exports and
  // performing other necessary setup
  /** @param {WebAssembly.Module=} module*/
  function receiveInstance(instance, module) {
    wasmExports = instance.exports;

    

    wasmMemory = wasmExports['memory'];
    
    assert(wasmMemory, "memory not found in wasm exports");
    // This assertion doesn't hold when emscripten is run in --post-link
    // mode.
    // TODO(sbc): Read INITIAL_MEMORY out of the wasm file in post-link mode.
    //assert(wasmMemory.buffer.byteLength === 16777216);
    updateMemoryViews();

    wasmTable = wasmExports['__indirect_function_table'];
    
    assert(wasmTable, "table not found in wasm exports");

    addOnInit(wasmExports['__wasm_call_ctors']);

    removeRunDependency('wasm-instantiate');
    return wasmExports;
  }
  // wait for the pthread pool (if any)
  addRunDependency('wasm-instantiate');

  // Prefer streaming instantiation if available.
  // Async compilation can be confusing when an error on the page overwrites Module
  // (for example, if the order of elements is wrong, and the one defining Module is
  // later), so we save Module and check it later.
  var trueModule = Module;
  function receiveInstantiationResult(result) {
    // 'result' is a ResultObject object which has both the module and instance.
    // receiveInstance() will swap in the exports (to Module.asm) so they can be called
    assert(Module === trueModule, 'the Module object should not be replaced during async compilation - perhaps the order of HTML elements is wrong?');
    trueModule = null;
    // TODO: Due to Closure regression https://github.com/google/closure-compiler/issues/3193, the above line no longer optimizes out down to the following line.
    // When the regression is fixed, can restore the above PTHREADS-enabled path.
    receiveInstance(result['instance']);
  }

  // User shell pages can write their own Module.instantiateWasm = function(imports, successCallback) callback
  // to manually instantiate the Wasm module themselves. This allows pages to
  // run the instantiation parallel to any other async startup actions they are
  // performing.
  // Also pthreads and wasm workers initialize the wasm instance through this
  // path.
  if (Module['instantiateWasm']) {

    try {
      return Module['instantiateWasm'](info, receiveInstance);
    } catch(e) {
      err(`Module.instantiateWasm callback failed with error: ${e}`);
        // If instantiation fails, reject the module ready promise.
        readyPromiseReject(e);
    }
  }

  // If instantiation fails, reject the module ready promise.
  instantiateAsync(wasmBinary, wasmBinaryFile, info, receiveInstantiationResult).catch(readyPromiseReject);
  return {}; // no exports yet; we'll fill them in later
}

// Globals used by JS i64 conversions (see makeSetValue)
var tempDouble;
var tempI64;

// include: runtime_debug.js
function legacyModuleProp(prop, newName, incomming=true) {
  if (!Object.getOwnPropertyDescriptor(Module, prop)) {
    Object.defineProperty(Module, prop, {
      configurable: true,
      get() {
        let extra = incomming ? ' (the initial value can be provided on Module, but after startup the value is only looked for on a local variable of that name)' : '';
        abort(`\`Module.${prop}\` has been replaced by \`${newName}\`` + extra);

      }
    });
  }
}

function ignoredModuleProp(prop) {
  if (Object.getOwnPropertyDescriptor(Module, prop)) {
    abort(`\`Module.${prop}\` was supplied but \`${prop}\` not included in INCOMING_MODULE_JS_API`);
  }
}

// forcing the filesystem exports a few things by default
function isExportedByForceFilesystem(name) {
  return name === 'FS_createPath' ||
         name === 'FS_createDataFile' ||
         name === 'FS_createPreloadedFile' ||
         name === 'FS_unlink' ||
         name === 'addRunDependency' ||
         // The old FS has some functionality that WasmFS lacks.
         name === 'FS_createLazyFile' ||
         name === 'FS_createDevice' ||
         name === 'removeRunDependency';
}

function missingGlobal(sym, msg) {
  if (typeof globalThis !== 'undefined') {
    Object.defineProperty(globalThis, sym, {
      configurable: true,
      get() {
        warnOnce('`' + sym + '` is not longer defined by emscripten. ' + msg);
        return undefined;
      }
    });
  }
}

missingGlobal('buffer', 'Please use HEAP8.buffer or wasmMemory.buffer');
missingGlobal('asm', 'Please use wasmExports instead');

function missingLibrarySymbol(sym) {
  if (typeof globalThis !== 'undefined' && !Object.getOwnPropertyDescriptor(globalThis, sym)) {
    Object.defineProperty(globalThis, sym, {
      configurable: true,
      get() {
        // Can't `abort()` here because it would break code that does runtime
        // checks.  e.g. `if (typeof SDL === 'undefined')`.
        var msg = '`' + sym + '` is a library symbol and not included by default; add it to your library.js __deps or to DEFAULT_LIBRARY_FUNCS_TO_INCLUDE on the command line';
        // DEFAULT_LIBRARY_FUNCS_TO_INCLUDE requires the name as it appears in
        // library.js, which means $name for a JS name with no prefix, or name
        // for a JS name like _name.
        var librarySymbol = sym;
        if (!librarySymbol.startsWith('_')) {
          librarySymbol = '$' + sym;
        }
        msg += " (e.g. -sDEFAULT_LIBRARY_FUNCS_TO_INCLUDE='" + librarySymbol + "')";
        if (isExportedByForceFilesystem(sym)) {
          msg += '. Alternatively, forcing filesystem support (-sFORCE_FILESYSTEM) can export this for you';
        }
        warnOnce(msg);
        return undefined;
      }
    });
  }
  // Any symbol that is not included from the JS libary is also (by definition)
  // not exported on the Module object.
  unexportedRuntimeSymbol(sym);
}

function unexportedRuntimeSymbol(sym) {
  if (!Object.getOwnPropertyDescriptor(Module, sym)) {
    Object.defineProperty(Module, sym, {
      configurable: true,
      get() {
        var msg = "'" + sym + "' was not exported. add it to EXPORTED_RUNTIME_METHODS (see the Emscripten FAQ)";
        if (isExportedByForceFilesystem(sym)) {
          msg += '. Alternatively, forcing filesystem support (-sFORCE_FILESYSTEM) can export this for you';
        }
        abort(msg);
      }
    });
  }
}

// Used by XXXXX_DEBUG settings to output debug messages.
function dbg(text) {
  // TODO(sbc): Make this configurable somehow.  Its not always convenient for
  // logging to show up as warnings.
  console.warn.apply(console, arguments);
}
// end include: runtime_debug.js
// === Body ===

// end include: preamble.js

  /** @constructor */
  function ExitStatus(status) {
      this.name = 'ExitStatus';
      this.message = `Program terminated with exit(${status})`;
      this.status = status;
    }

  var callRuntimeCallbacks = (callbacks) => {
      while (callbacks.length > 0) {
        // Pass the module as the first argument.
        callbacks.shift()(Module);
      }
    };

  
    /**
     * @param {number} ptr
     * @param {string} type
     */
  function getValue(ptr, type = 'i8') {
    if (type.endsWith('*')) type = '*';
    switch (type) {
      case 'i1': return HEAP8[((ptr)>>0)];
      case 'i8': return HEAP8[((ptr)>>0)];
      case 'i16': return HEAP16[((ptr)>>1)];
      case 'i32': return HEAP32[((ptr)>>2)];
      case 'i64': abort('to do getValue(i64) use WASM_BIGINT');
      case 'float': return HEAPF32[((ptr)>>2)];
      case 'double': return HEAPF64[((ptr)>>3)];
      case '*': return HEAPU32[((ptr)>>2)];
      default: abort(`invalid type for getValue: ${type}`);
    }
  }

  var noExitRuntime = Module['noExitRuntime'] || true;

  var ptrToString = (ptr) => {
      assert(typeof ptr === 'number');
      // With CAN_ADDRESS_2GB or MEMORY64, pointers are already unsigned.
      ptr >>>= 0;
      return '0x' + ptr.toString(16).padStart(8, '0');
    };

  
    /**
     * @param {number} ptr
     * @param {number} value
     * @param {string} type
     */
  function setValue(ptr, value, type = 'i8') {
    if (type.endsWith('*')) type = '*';
    switch (type) {
      case 'i1': HEAP8[((ptr)>>0)] = value; break;
      case 'i8': HEAP8[((ptr)>>0)] = value; break;
      case 'i16': HEAP16[((ptr)>>1)] = value; break;
      case 'i32': HEAP32[((ptr)>>2)] = value; break;
      case 'i64': abort('to do setValue(i64) use WASM_BIGINT');
      case 'float': HEAPF32[((ptr)>>2)] = value; break;
      case 'double': HEAPF64[((ptr)>>3)] = value; break;
      case '*': HEAPU32[((ptr)>>2)] = value; break;
      default: abort(`invalid type for setValue: ${type}`);
    }
  }

  var warnOnce = (text) => {
      if (!warnOnce.shown) warnOnce.shown = {};
      if (!warnOnce.shown[text]) {
        warnOnce.shown[text] = 1;
        if (ENVIRONMENT_IS_NODE) text = 'warning: ' + text;
        err(text);
      }
    };

  /** @constructor */
  function ExceptionInfo(excPtr) {
      this.excPtr = excPtr;
      this.ptr = excPtr - 24;
  
      this.set_type = function(type) {
        HEAPU32[(((this.ptr)+(4))>>2)] = type;
      };
  
      this.get_type = function() {
        return HEAPU32[(((this.ptr)+(4))>>2)];
      };
  
      this.set_destructor = function(destructor) {
        HEAPU32[(((this.ptr)+(8))>>2)] = destructor;
      };
  
      this.get_destructor = function() {
        return HEAPU32[(((this.ptr)+(8))>>2)];
      };
  
      this.set_caught = function(caught) {
        caught = caught ? 1 : 0;
        HEAP8[(((this.ptr)+(12))>>0)] = caught;
      };
  
      this.get_caught = function() {
        return HEAP8[(((this.ptr)+(12))>>0)] != 0;
      };
  
      this.set_rethrown = function(rethrown) {
        rethrown = rethrown ? 1 : 0;
        HEAP8[(((this.ptr)+(13))>>0)] = rethrown;
      };
  
      this.get_rethrown = function() {
        return HEAP8[(((this.ptr)+(13))>>0)] != 0;
      };
  
      // Initialize native structure fields. Should be called once after allocated.
      this.init = function(type, destructor) {
        this.set_adjusted_ptr(0);
        this.set_type(type);
        this.set_destructor(destructor);
      }
  
      this.set_adjusted_ptr = function(adjustedPtr) {
        HEAPU32[(((this.ptr)+(16))>>2)] = adjustedPtr;
      };
  
      this.get_adjusted_ptr = function() {
        return HEAPU32[(((this.ptr)+(16))>>2)];
      };
  
      // Get pointer which is expected to be received by catch clause in C++ code. It may be adjusted
      // when the pointer is casted to some of the exception object base classes (e.g. when virtual
      // inheritance is used). When a pointer is thrown this method should return the thrown pointer
      // itself.
      this.get_exception_ptr = function() {
        // Work around a fastcomp bug, this code is still included for some reason in a build without
        // exceptions support.
        var isPointer = ___cxa_is_pointer_type(this.get_type());
        if (isPointer) {
          return HEAPU32[((this.excPtr)>>2)];
        }
        var adjusted = this.get_adjusted_ptr();
        if (adjusted !== 0) return adjusted;
        return this.excPtr;
      };
    }
  
  var exceptionLast = 0;
  
  var uncaughtExceptionCount = 0;
  var ___cxa_throw = (ptr, type, destructor) => {
      var info = new ExceptionInfo(ptr);
      // Initialize ExceptionInfo content after it was allocated in __cxa_allocate_exception.
      info.init(type, destructor);
      exceptionLast = ptr;
      uncaughtExceptionCount++;
      assert(false, 'Exception thrown, but exception catching is not enabled. Compile with -sNO_DISABLE_EXCEPTION_CATCHING or -sEXCEPTION_CATCHING_ALLOWED=[..] to catch.');
    };

  var __embind_register_bigint = (primitiveType, name, size, minRange, maxRange) => {};

  var embind_init_charCodes = () => {
      var codes = new Array(256);
      for (var i = 0; i < 256; ++i) {
          codes[i] = String.fromCharCode(i);
      }
      embind_charCodes = codes;
    };
  var embind_charCodes;
  var readLatin1String = (ptr) => {
      var ret = "";
      var c = ptr;
      while (HEAPU8[c]) {
          ret += embind_charCodes[HEAPU8[c++]];
      }
      return ret;
    };
  
  var awaitingDependencies = {
  };
  
  var registeredTypes = {
  };
  
  var typeDependencies = {
  };
  
  var BindingError;
  var throwBindingError = (message) => { throw new BindingError(message); };
  
  
  
  
  var InternalError;
  var throwInternalError = (message) => { throw new InternalError(message); };
  var whenDependentTypesAreResolved = (myTypes, dependentTypes, getTypeConverters) => {
      myTypes.forEach(function(type) {
          typeDependencies[type] = dependentTypes;
      });
  
      function onComplete(typeConverters) {
          var myTypeConverters = getTypeConverters(typeConverters);
          if (myTypeConverters.length !== myTypes.length) {
              throwInternalError('Mismatched type converter count');
          }
          for (var i = 0; i < myTypes.length; ++i) {
              registerType(myTypes[i], myTypeConverters[i]);
          }
      }
  
      var typeConverters = new Array(dependentTypes.length);
      var unregisteredTypes = [];
      var registered = 0;
      dependentTypes.forEach((dt, i) => {
        if (registeredTypes.hasOwnProperty(dt)) {
          typeConverters[i] = registeredTypes[dt];
        } else {
          unregisteredTypes.push(dt);
          if (!awaitingDependencies.hasOwnProperty(dt)) {
            awaitingDependencies[dt] = [];
          }
          awaitingDependencies[dt].push(() => {
            typeConverters[i] = registeredTypes[dt];
            ++registered;
            if (registered === unregisteredTypes.length) {
              onComplete(typeConverters);
            }
          });
        }
      });
      if (0 === unregisteredTypes.length) {
        onComplete(typeConverters);
      }
    };
  /** @param {Object=} options */
  function sharedRegisterType(rawType, registeredInstance, options = {}) {
      var name = registeredInstance.name;
      if (!rawType) {
        throwBindingError(`type "${name}" must have a positive integer typeid pointer`);
      }
      if (registeredTypes.hasOwnProperty(rawType)) {
        if (options.ignoreDuplicateRegistrations) {
          return;
        } else {
          throwBindingError(`Cannot register type '${name}' twice`);
        }
      }
  
      registeredTypes[rawType] = registeredInstance;
      delete typeDependencies[rawType];
  
      if (awaitingDependencies.hasOwnProperty(rawType)) {
        var callbacks = awaitingDependencies[rawType];
        delete awaitingDependencies[rawType];
        callbacks.forEach((cb) => cb());
      }
    }
  /** @param {Object=} options */
  function registerType(rawType, registeredInstance, options = {}) {
      if (!('argPackAdvance' in registeredInstance)) {
        throw new TypeError('registerType registeredInstance requires argPackAdvance');
      }
      return sharedRegisterType(rawType, registeredInstance, options);
    }
  
  var GenericWireTypeSize = 8;
  /** @suppress {globalThis} */
  var __embind_register_bool = (rawType, name, trueValue, falseValue) => {
      name = readLatin1String(name);
      registerType(rawType, {
          name,
          'fromWireType': function(wt) {
              // ambiguous emscripten ABI: sometimes return values are
              // true or false, and sometimes integers (0 or 1)
              return !!wt;
          },
          'toWireType': function(destructors, o) {
              return o ? trueValue : falseValue;
          },
          'argPackAdvance': GenericWireTypeSize,
          'readValueFromPointer': function(pointer) {
              return this['fromWireType'](HEAPU8[pointer]);
          },
          destructorFunction: null, // This type does not need a destructor
      });
    };

  function handleAllocatorInit() {
      Object.assign(HandleAllocator.prototype, /** @lends {HandleAllocator.prototype} */ {
        get(id) {
          assert(this.allocated[id] !== undefined, `invalid handle: ${id}`);
          return this.allocated[id];
        },
        has(id) {
          return this.allocated[id] !== undefined;
        },
        allocate(handle) {
          var id = this.freelist.pop() || this.allocated.length;
          this.allocated[id] = handle;
          return id;
        },
        free(id) {
          assert(this.allocated[id] !== undefined);
          // Set the slot to `undefined` rather than using `delete` here since
          // apparently arrays with holes in them can be less efficient.
          this.allocated[id] = undefined;
          this.freelist.push(id);
        }
      });
    }
  /** @constructor */
  function HandleAllocator() {
      // Reserve slot 0 so that 0 is always an invalid handle
      this.allocated = [undefined];
      this.freelist = [];
    }
  var emval_handles = new HandleAllocator();;
  var __emval_decref = (handle) => {
      if (handle >= emval_handles.reserved && 0 === --emval_handles.get(handle).refcount) {
        emval_handles.free(handle);
      }
    };
  
  
  
  var count_emval_handles = () => {
      var count = 0;
      for (var i = emval_handles.reserved; i < emval_handles.allocated.length; ++i) {
        if (emval_handles.allocated[i] !== undefined) {
          ++count;
        }
      }
      return count;
    };
  
  var init_emval = () => {
      // reserve some special values. These never get de-allocated.
      // The HandleAllocator takes care of reserving zero.
      emval_handles.allocated.push(
        {value: undefined},
        {value: null},
        {value: true},
        {value: false},
      );
      emval_handles.reserved = emval_handles.allocated.length
      Module['count_emval_handles'] = count_emval_handles;
    };
  var Emval = {
  toValue:(handle) => {
        if (!handle) {
            throwBindingError('Cannot use deleted val. handle = ' + handle);
        }
        return emval_handles.get(handle).value;
      },
  toHandle:(value) => {
        switch (value) {
          case undefined: return 1;
          case null: return 2;
          case true: return 3;
          case false: return 4;
          default:{
            return emval_handles.allocate({refcount: 1, value: value});
          }
        }
      },
  };
  
  
  
  /** @suppress {globalThis} */
  function simpleReadValueFromPointer(pointer) {
      return this['fromWireType'](HEAP32[((pointer)>>2)]);
    }
  var __embind_register_emval = (rawType, name) => {
      name = readLatin1String(name);
      registerType(rawType, {
        name,
        'fromWireType': (handle) => {
          var rv = Emval.toValue(handle);
          __emval_decref(handle);
          return rv;
        },
        'toWireType': (destructors, value) => Emval.toHandle(value),
        'argPackAdvance': GenericWireTypeSize,
        'readValueFromPointer': simpleReadValueFromPointer,
        destructorFunction: null, // This type does not need a destructor
  
        // TODO: do we need a deleteObject here?  write a test where
        // emval is passed into JS via an interface
      });
    };

  var embindRepr = (v) => {
      if (v === null) {
          return 'null';
      }
      var t = typeof v;
      if (t === 'object' || t === 'array' || t === 'function') {
          return v.toString();
      } else {
          return '' + v;
      }
    };
  
  var floatReadValueFromPointer = (name, width) => {
      switch (width) {
          case 4: return function(pointer) {
              return this['fromWireType'](HEAPF32[((pointer)>>2)]);
          };
          case 8: return function(pointer) {
              return this['fromWireType'](HEAPF64[((pointer)>>3)]);
          };
          default:
              throw new TypeError(`invalid float width (${width}): ${name}`);
      }
    };
  
  
  var __embind_register_float = (rawType, name, size) => {
      name = readLatin1String(name);
      registerType(rawType, {
        name,
        'fromWireType': (value) => value,
        'toWireType': (destructors, value) => {
          if (typeof value != "number" && typeof value != "boolean") {
            throw new TypeError(`Cannot convert ${embindRepr(value)} to ${this.name}`);
          }
          // The VM will perform JS to Wasm value conversion, according to the spec:
          // https://www.w3.org/TR/wasm-js-api-1/#towebassemblyvalue
          return value;
        },
        'argPackAdvance': GenericWireTypeSize,
        'readValueFromPointer': floatReadValueFromPointer(name, size),
        destructorFunction: null, // This type does not need a destructor
      });
    };

  var createNamedFunction = (name, body) => Object.defineProperty(body, 'name', {
      value: name
    });
  
  var runDestructors = (destructors) => {
      while (destructors.length) {
        var ptr = destructors.pop();
        var del = destructors.pop();
        del(ptr);
      }
    };
  
  
  function newFunc(constructor, argumentList) {
      if (!(constructor instanceof Function)) {
        throw new TypeError(`new_ called with constructor type ${typeof(constructor)} which is not a function`);
      }
      /*
       * Previously, the following line was just:
       *   function dummy() {};
       * Unfortunately, Chrome was preserving 'dummy' as the object's name, even
       * though at creation, the 'dummy' has the correct constructor name.  Thus,
       * objects created with IMVU.new would show up in the debugger as 'dummy',
       * which isn't very helpful.  Using IMVU.createNamedFunction addresses the
       * issue.  Doublely-unfortunately, there's no way to write a test for this
       * behavior.  -NRD 2013.02.22
       */
      var dummy = createNamedFunction(constructor.name || 'unknownFunctionName', function(){});
      dummy.prototype = constructor.prototype;
      var obj = new dummy;
  
      var r = constructor.apply(obj, argumentList);
      return (r instanceof Object) ? r : obj;
    }
  function craftInvokerFunction(humanName, argTypes, classType, cppInvokerFunc, cppTargetFunc, /** boolean= */ isAsync) {
      // humanName: a human-readable string name for the function to be generated.
      // argTypes: An array that contains the embind type objects for all types in the function signature.
      //    argTypes[0] is the type object for the function return value.
      //    argTypes[1] is the type object for function this object/class type, or null if not crafting an invoker for a class method.
      //    argTypes[2...] are the actual function parameters.
      // classType: The embind type object for the class to be bound, or null if this is not a method of a class.
      // cppInvokerFunc: JS Function object to the C++-side function that interops into C++ code.
      // cppTargetFunc: Function pointer (an integer to FUNCTION_TABLE) to the target C++ function the cppInvokerFunc will end up calling.
      // isAsync: Optional. If true, returns an async function. Async bindings are only supported with JSPI.
      var argCount = argTypes.length;
  
      if (argCount < 2) {
        throwBindingError("argTypes array size mismatch! Must at least get return value and 'this' types!");
      }
  
      assert(!isAsync, 'Async bindings are only supported with JSPI.');
  
      var isClassMethodFunc = (argTypes[1] !== null && classType !== null);
  
      // Free functions with signature "void function()" do not need an invoker that marshalls between wire types.
  // TODO: This omits argument count check - enable only at -O3 or similar.
  //    if (ENABLE_UNSAFE_OPTS && argCount == 2 && argTypes[0].name == "void" && !isClassMethodFunc) {
  //       return FUNCTION_TABLE[fn];
  //    }
  
      // Determine if we need to use a dynamic stack to store the destructors for the function parameters.
      // TODO: Remove this completely once all function invokers are being dynamically generated.
      var needsDestructorStack = false;
  
      for (var i = 1; i < argTypes.length; ++i) { // Skip return value at index 0 - it's not deleted here.
        if (argTypes[i] !== null && argTypes[i].destructorFunction === undefined) { // The type does not define a destructor function - must use dynamic stack
          needsDestructorStack = true;
          break;
        }
      }
  
      var returns = (argTypes[0].name !== "void");
  
      var argsList = "";
      var argsListWired = "";
      for (var i = 0; i < argCount - 2; ++i) {
        argsList += (i!==0?", ":"")+"arg"+i;
        argsListWired += (i!==0?", ":"")+"arg"+i+"Wired";
      }
  
      var invokerFnBody = `
        return function (${argsList}) {
        if (arguments.length !== ${argCount - 2}) {
          throwBindingError('function ${humanName} called with ' + arguments.length + ' arguments, expected ${argCount - 2}');
        }`;
  
      if (needsDestructorStack) {
        invokerFnBody += "var destructors = [];\n";
      }
  
      var dtorStack = needsDestructorStack ? "destructors" : "null";
      var args1 = ["throwBindingError", "invoker", "fn", "runDestructors", "retType", "classParam"];
      var args2 = [throwBindingError, cppInvokerFunc, cppTargetFunc, runDestructors, argTypes[0], argTypes[1]];
  
      if (isClassMethodFunc) {
        invokerFnBody += "var thisWired = classParam.toWireType("+dtorStack+", this);\n";
      }
  
      for (var i = 0; i < argCount - 2; ++i) {
        invokerFnBody += "var arg"+i+"Wired = argType"+i+".toWireType("+dtorStack+", arg"+i+"); // "+argTypes[i+2].name+"\n";
        args1.push("argType"+i);
        args2.push(argTypes[i+2]);
      }
  
      if (isClassMethodFunc) {
        argsListWired = "thisWired" + (argsListWired.length > 0 ? ", " : "") + argsListWired;
      }
  
      invokerFnBody +=
          (returns || isAsync ? "var rv = ":"") + "invoker(fn"+(argsListWired.length>0?", ":"")+argsListWired+");\n";
  
      if (needsDestructorStack) {
        invokerFnBody += "runDestructors(destructors);\n";
      } else {
        for (var i = isClassMethodFunc?1:2; i < argTypes.length; ++i) { // Skip return value at index 0 - it's not deleted here. Also skip class type if not a method.
          var paramName = (i === 1 ? "thisWired" : ("arg"+(i - 2)+"Wired"));
          if (argTypes[i].destructorFunction !== null) {
            invokerFnBody += paramName+"_dtor("+paramName+"); // "+argTypes[i].name+"\n";
            args1.push(paramName+"_dtor");
            args2.push(argTypes[i].destructorFunction);
          }
        }
      }
  
      if (returns) {
        invokerFnBody += "var ret = retType.fromWireType(rv);\n" +
                         "return ret;\n";
      } else {
      }
  
      invokerFnBody += "}\n";
  
      args1.push(invokerFnBody);
  
      var invokerFn = newFunc(Function, args1).apply(null, args2);
      return createNamedFunction(humanName, invokerFn);
    }
  
  var ensureOverloadTable = (proto, methodName, humanName) => {
      if (undefined === proto[methodName].overloadTable) {
        var prevFunc = proto[methodName];
        // Inject an overload resolver function that routes to the appropriate overload based on the number of arguments.
        proto[methodName] = function() {
          // TODO This check can be removed in -O3 level "unsafe" optimizations.
          if (!proto[methodName].overloadTable.hasOwnProperty(arguments.length)) {
              throwBindingError(`Function '${humanName}' called with an invalid number of arguments (${arguments.length}) - expects one of (${proto[methodName].overloadTable})!`);
          }
          return proto[methodName].overloadTable[arguments.length].apply(this, arguments);
        };
        // Move the previous function into the overload table.
        proto[methodName].overloadTable = [];
        proto[methodName].overloadTable[prevFunc.argCount] = prevFunc;
      }
    };
  
  /** @param {number=} numArguments */
  var exposePublicSymbol = (name, value, numArguments) => {
      if (Module.hasOwnProperty(name)) {
        if (undefined === numArguments || (undefined !== Module[name].overloadTable && undefined !== Module[name].overloadTable[numArguments])) {
          throwBindingError(`Cannot register public name '${name}' twice`);
        }
  
        // We are exposing a function with the same name as an existing function. Create an overload table and a function selector
        // that routes between the two.
        ensureOverloadTable(Module, name, name);
        if (Module.hasOwnProperty(numArguments)) {
          throwBindingError(`Cannot register multiple overloads of a function with the same number of arguments (${numArguments})!`);
        }
        // Add the new function into the overload table.
        Module[name].overloadTable[numArguments] = value;
      }
      else {
        Module[name] = value;
        if (undefined !== numArguments) {
          Module[name].numArguments = numArguments;
        }
      }
    };
  
  var heap32VectorToArray = (count, firstElement) => {
      var array = [];
      for (var i = 0; i < count; i++) {
          // TODO(https://github.com/emscripten-core/emscripten/issues/17310):
          // Find a way to hoist the `>> 2` or `>> 3` out of this loop.
          array.push(HEAPU32[(((firstElement)+(i * 4))>>2)]);
      }
      return array;
    };
  
  
  /** @param {number=} numArguments */
  var replacePublicSymbol = (name, value, numArguments) => {
      if (!Module.hasOwnProperty(name)) {
        throwInternalError('Replacing nonexistant public symbol');
      }
      // If there's an overload table for this symbol, replace the symbol in the overload table instead.
      if (undefined !== Module[name].overloadTable && undefined !== numArguments) {
        Module[name].overloadTable[numArguments] = value;
      }
      else {
        Module[name] = value;
        Module[name].argCount = numArguments;
      }
    };
  
  
  
  var dynCallLegacy = (sig, ptr, args) => {
      assert(('dynCall_' + sig) in Module, `bad function pointer type - dynCall function not found for sig '${sig}'`);
      if (args && args.length) {
        // j (64-bit integer) must be passed in as two numbers [low 32, high 32].
        assert(args.length === sig.substring(1).replace(/j/g, '--').length);
      } else {
        assert(sig.length == 1);
      }
      var f = Module['dynCall_' + sig];
      return args && args.length ? f.apply(null, [ptr].concat(args)) : f.call(null, ptr);
    };
  
  var wasmTableMirror = [];
  
  var wasmTable;
  var getWasmTableEntry = (funcPtr) => {
      var func = wasmTableMirror[funcPtr];
      if (!func) {
        if (funcPtr >= wasmTableMirror.length) wasmTableMirror.length = funcPtr + 1;
        wasmTableMirror[funcPtr] = func = wasmTable.get(funcPtr);
      }
      assert(wasmTable.get(funcPtr) == func, "JavaScript-side Wasm function table mirror is out of date!");
      return func;
    };
  
  /** @param {Object=} args */
  var dynCall = (sig, ptr, args) => {
      // Without WASM_BIGINT support we cannot directly call function with i64 as
      // part of thier signature, so we rely the dynCall functions generated by
      // wasm-emscripten-finalize
      if (sig.includes('j')) {
        return dynCallLegacy(sig, ptr, args);
      }
      assert(getWasmTableEntry(ptr), `missing table entry in dynCall: ${ptr}`);
      var rtn = getWasmTableEntry(ptr).apply(null, args);
      return rtn;
    };
  var getDynCaller = (sig, ptr) => {
      assert(sig.includes('j') || sig.includes('p'), 'getDynCaller should only be called with i64 sigs')
      var argCache = [];
      return function() {
        argCache.length = 0;
        Object.assign(argCache, arguments);
        return dynCall(sig, ptr, argCache);
      };
    };
  
  
  var embind__requireFunction = (signature, rawFunction) => {
      signature = readLatin1String(signature);
  
      function makeDynCaller() {
        if (signature.includes('j')) {
          return getDynCaller(signature, rawFunction);
        }
        return getWasmTableEntry(rawFunction);
      }
  
      var fp = makeDynCaller();
      if (typeof fp != "function") {
          throwBindingError(`unknown function pointer with signature ${signature}: ${rawFunction}`);
      }
      return fp;
    };
  
  
  
  var extendError = (baseErrorType, errorName) => {
      var errorClass = createNamedFunction(errorName, function(message) {
        this.name = errorName;
        this.message = message;
  
        var stack = (new Error(message)).stack;
        if (stack !== undefined) {
          this.stack = this.toString() + '\n' +
              stack.replace(/^Error(:[^\n]*)?\n/, '');
        }
      });
      errorClass.prototype = Object.create(baseErrorType.prototype);
      errorClass.prototype.constructor = errorClass;
      errorClass.prototype.toString = function() {
        if (this.message === undefined) {
          return this.name;
        } else {
          return `${this.name}: ${this.message}`;
        }
      };
  
      return errorClass;
    };
  var UnboundTypeError;
  
  
  
  var getTypeName = (type) => {
      var ptr = ___getTypeName(type);
      var rv = readLatin1String(ptr);
      _free(ptr);
      return rv;
    };
  var throwUnboundTypeError = (message, types) => {
      var unboundTypes = [];
      var seen = {};
      function visit(type) {
        if (seen[type]) {
          return;
        }
        if (registeredTypes[type]) {
          return;
        }
        if (typeDependencies[type]) {
          typeDependencies[type].forEach(visit);
          return;
        }
        unboundTypes.push(type);
        seen[type] = true;
      }
      types.forEach(visit);
  
      throw new UnboundTypeError(`${message}: ` + unboundTypes.map(getTypeName).join([', ']));
    };
  
  
  var getFunctionName = (signature) => {
      signature = signature.trim();
      const argsIndex = signature.indexOf("(");
      if (argsIndex !== -1) {
        assert(signature[signature.length - 1] == ")", "Parentheses for argument names should match.");
        return signature.substr(0, argsIndex);
      } else {
        return signature;
      }
    };
  var __embind_register_function = (name, argCount, rawArgTypesAddr, signature, rawInvoker, fn, isAsync) => {
      var argTypes = heap32VectorToArray(argCount, rawArgTypesAddr);
      name = readLatin1String(name);
      name = getFunctionName(name);
  
      rawInvoker = embind__requireFunction(signature, rawInvoker);
  
      exposePublicSymbol(name, function() {
        throwUnboundTypeError(`Cannot call ${name} due to unbound types`, argTypes);
      }, argCount - 1);
  
      whenDependentTypesAreResolved([], argTypes, function(argTypes) {
        var invokerArgsArray = [argTypes[0] /* return value */, null /* no class 'this'*/].concat(argTypes.slice(1) /* actual params */);
        replacePublicSymbol(name, craftInvokerFunction(name, invokerArgsArray, null /* no class 'this'*/, rawInvoker, fn, isAsync), argCount - 1);
        return [];
      });
    };

  
  var integerReadValueFromPointer = (name, width, signed) => {
      // integers are quite common, so generate very specialized functions
      switch (width) {
          case 1: return signed ?
              (pointer) => HEAP8[((pointer)>>0)] :
              (pointer) => HEAPU8[((pointer)>>0)];
          case 2: return signed ?
              (pointer) => HEAP16[((pointer)>>1)] :
              (pointer) => HEAPU16[((pointer)>>1)]
          case 4: return signed ?
              (pointer) => HEAP32[((pointer)>>2)] :
              (pointer) => HEAPU32[((pointer)>>2)]
          default:
              throw new TypeError(`invalid integer width (${width}): ${name}`);
      }
    };
  
  
  /** @suppress {globalThis} */
  var __embind_register_integer = (primitiveType, name, size, minRange, maxRange) => {
      name = readLatin1String(name);
      // LLVM doesn't have signed and unsigned 32-bit types, so u32 literals come
      // out as 'i32 -1'. Always treat those as max u32.
      if (maxRange === -1) {
        maxRange = 4294967295;
      }
  
      var fromWireType = (value) => value;
  
      if (minRange === 0) {
        var bitshift = 32 - 8*size;
        fromWireType = (value) => (value << bitshift) >>> bitshift;
      }
  
      var isUnsignedType = (name.includes('unsigned'));
      var checkAssertions = (value, toTypeName) => {
        if (typeof value != "number" && typeof value != "boolean") {
          throw new TypeError(`Cannot convert "${embindRepr(value)}" to ${toTypeName}`);
        }
        if (value < minRange || value > maxRange) {
          throw new TypeError(`Passing a number "${embindRepr(value)}" from JS side to C/C++ side to an argument of type "${name}", which is outside the valid range [${minRange}, ${maxRange}]!`);
        }
      }
      var toWireType;
      if (isUnsignedType) {
        toWireType = function(destructors, value) {
          checkAssertions(value, this.name);
          return value >>> 0;
        }
      } else {
        toWireType = function(destructors, value) {
          checkAssertions(value, this.name);
          // The VM will perform JS to Wasm value conversion, according to the spec:
          // https://www.w3.org/TR/wasm-js-api-1/#towebassemblyvalue
          return value;
        }
      }
      registerType(primitiveType, {
        name,
        'fromWireType': fromWireType,
        'toWireType': toWireType,
        'argPackAdvance': GenericWireTypeSize,
        'readValueFromPointer': integerReadValueFromPointer(name, size, minRange !== 0),
        destructorFunction: null, // This type does not need a destructor
      });
    };

  
  var __embind_register_memory_view = (rawType, dataTypeIndex, name) => {
      var typeMapping = [
        Int8Array,
        Uint8Array,
        Int16Array,
        Uint16Array,
        Int32Array,
        Uint32Array,
        Float32Array,
        Float64Array,
      ];
  
      var TA = typeMapping[dataTypeIndex];
  
      function decodeMemoryView(handle) {
        var size = HEAPU32[((handle)>>2)];
        var data = HEAPU32[(((handle)+(4))>>2)];
        return new TA(HEAP8.buffer, data, size);
      }
  
      name = readLatin1String(name);
      registerType(rawType, {
        name,
        'fromWireType': decodeMemoryView,
        'argPackAdvance': GenericWireTypeSize,
        'readValueFromPointer': decodeMemoryView,
      }, {
        ignoreDuplicateRegistrations: true,
      });
    };

  
  
  /** @suppress {globalThis} */
  function readPointer(pointer) {
      return this['fromWireType'](HEAPU32[((pointer)>>2)]);
    }
  
  
  var stringToUTF8Array = (str, heap, outIdx, maxBytesToWrite) => {
      assert(typeof str === 'string', `stringToUTF8Array expects a string (got ${typeof str})`);
      // Parameter maxBytesToWrite is not optional. Negative values, 0, null,
      // undefined and false each don't write out any bytes.
      if (!(maxBytesToWrite > 0))
        return 0;
  
      var startIdx = outIdx;
      var endIdx = outIdx + maxBytesToWrite - 1; // -1 for string null terminator.
      for (var i = 0; i < str.length; ++i) {
        // Gotcha: charCodeAt returns a 16-bit word that is a UTF-16 encoded code
        // unit, not a Unicode code point of the character! So decode
        // UTF16->UTF32->UTF8.
        // See http://unicode.org/faq/utf_bom.html#utf16-3
        // For UTF8 byte structure, see http://en.wikipedia.org/wiki/UTF-8#Description
        // and https://www.ietf.org/rfc/rfc2279.txt
        // and https://tools.ietf.org/html/rfc3629
        var u = str.charCodeAt(i); // possibly a lead surrogate
        if (u >= 0xD800 && u <= 0xDFFF) {
          var u1 = str.charCodeAt(++i);
          u = 0x10000 + ((u & 0x3FF) << 10) | (u1 & 0x3FF);
        }
        if (u <= 0x7F) {
          if (outIdx >= endIdx) break;
          heap[outIdx++] = u;
        } else if (u <= 0x7FF) {
          if (outIdx + 1 >= endIdx) break;
          heap[outIdx++] = 0xC0 | (u >> 6);
          heap[outIdx++] = 0x80 | (u & 63);
        } else if (u <= 0xFFFF) {
          if (outIdx + 2 >= endIdx) break;
          heap[outIdx++] = 0xE0 | (u >> 12);
          heap[outIdx++] = 0x80 | ((u >> 6) & 63);
          heap[outIdx++] = 0x80 | (u & 63);
        } else {
          if (outIdx + 3 >= endIdx) break;
          if (u > 0x10FFFF) warnOnce('Invalid Unicode code point ' + ptrToString(u) + ' encountered when serializing a JS string to a UTF-8 string in wasm memory! (Valid unicode code points should be in range 0-0x10FFFF).');
          heap[outIdx++] = 0xF0 | (u >> 18);
          heap[outIdx++] = 0x80 | ((u >> 12) & 63);
          heap[outIdx++] = 0x80 | ((u >> 6) & 63);
          heap[outIdx++] = 0x80 | (u & 63);
        }
      }
      // Null-terminate the pointer to the buffer.
      heap[outIdx] = 0;
      return outIdx - startIdx;
    };
  var stringToUTF8 = (str, outPtr, maxBytesToWrite) => {
      assert(typeof maxBytesToWrite == 'number', 'stringToUTF8(str, outPtr, maxBytesToWrite) is missing the third parameter that specifies the length of the output buffer!');
      return stringToUTF8Array(str, HEAPU8, outPtr, maxBytesToWrite);
    };
  
  var lengthBytesUTF8 = (str) => {
      var len = 0;
      for (var i = 0; i < str.length; ++i) {
        // Gotcha: charCodeAt returns a 16-bit word that is a UTF-16 encoded code
        // unit, not a Unicode code point of the character! So decode
        // UTF16->UTF32->UTF8.
        // See http://unicode.org/faq/utf_bom.html#utf16-3
        var c = str.charCodeAt(i); // possibly a lead surrogate
        if (c <= 0x7F) {
          len++;
        } else if (c <= 0x7FF) {
          len += 2;
        } else if (c >= 0xD800 && c <= 0xDFFF) {
          len += 4; ++i;
        } else {
          len += 3;
        }
      }
      return len;
    };
  
  
  
  var UTF8Decoder = typeof TextDecoder != 'undefined' ? new TextDecoder('utf8') : undefined;
  
    /**
     * Given a pointer 'idx' to a null-terminated UTF8-encoded string in the given
     * array that contains uint8 values, returns a copy of that string as a
     * Javascript String object.
     * heapOrArray is either a regular array, or a JavaScript typed array view.
     * @param {number} idx
     * @param {number=} maxBytesToRead
     * @return {string}
     */
  var UTF8ArrayToString = (heapOrArray, idx, maxBytesToRead) => {
      var endIdx = idx + maxBytesToRead;
      var endPtr = idx;
      // TextDecoder needs to know the byte length in advance, it doesn't stop on
      // null terminator by itself.  Also, use the length info to avoid running tiny
      // strings through TextDecoder, since .subarray() allocates garbage.
      // (As a tiny code save trick, compare endPtr against endIdx using a negation,
      // so that undefined means Infinity)
      while (heapOrArray[endPtr] && !(endPtr >= endIdx)) ++endPtr;
  
      if (endPtr - idx > 16 && heapOrArray.buffer && UTF8Decoder) {
        return UTF8Decoder.decode(heapOrArray.subarray(idx, endPtr));
      }
      var str = '';
      // If building with TextDecoder, we have already computed the string length
      // above, so test loop end condition against that
      while (idx < endPtr) {
        // For UTF8 byte structure, see:
        // http://en.wikipedia.org/wiki/UTF-8#Description
        // https://www.ietf.org/rfc/rfc2279.txt
        // https://tools.ietf.org/html/rfc3629
        var u0 = heapOrArray[idx++];
        if (!(u0 & 0x80)) { str += String.fromCharCode(u0); continue; }
        var u1 = heapOrArray[idx++] & 63;
        if ((u0 & 0xE0) == 0xC0) { str += String.fromCharCode(((u0 & 31) << 6) | u1); continue; }
        var u2 = heapOrArray[idx++] & 63;
        if ((u0 & 0xF0) == 0xE0) {
          u0 = ((u0 & 15) << 12) | (u1 << 6) | u2;
        } else {
          if ((u0 & 0xF8) != 0xF0) warnOnce('Invalid UTF-8 leading byte ' + ptrToString(u0) + ' encountered when deserializing a UTF-8 string in wasm memory to a JS string!');
          u0 = ((u0 & 7) << 18) | (u1 << 12) | (u2 << 6) | (heapOrArray[idx++] & 63);
        }
  
        if (u0 < 0x10000) {
          str += String.fromCharCode(u0);
        } else {
          var ch = u0 - 0x10000;
          str += String.fromCharCode(0xD800 | (ch >> 10), 0xDC00 | (ch & 0x3FF));
        }
      }
      return str;
    };
  
    /**
     * Given a pointer 'ptr' to a null-terminated UTF8-encoded string in the
     * emscripten HEAP, returns a copy of that string as a Javascript String object.
     *
     * @param {number} ptr
     * @param {number=} maxBytesToRead - An optional length that specifies the
     *   maximum number of bytes to read. You can omit this parameter to scan the
     *   string until the first 0 byte. If maxBytesToRead is passed, and the string
     *   at [ptr, ptr+maxBytesToReadr[ contains a null byte in the middle, then the
     *   string will cut short at that byte index (i.e. maxBytesToRead will not
     *   produce a string of exact length [ptr, ptr+maxBytesToRead[) N.B. mixing
     *   frequent uses of UTF8ToString() with and without maxBytesToRead may throw
     *   JS JIT optimizations off, so it is worth to consider consistently using one
     * @return {string}
     */
  var UTF8ToString = (ptr, maxBytesToRead) => {
      assert(typeof ptr == 'number', `UTF8ToString expects a number (got ${typeof ptr})`);
      return ptr ? UTF8ArrayToString(HEAPU8, ptr, maxBytesToRead) : '';
    };
  var __embind_register_std_string = (rawType, name) => {
      name = readLatin1String(name);
      var stdStringIsUTF8
      //process only std::string bindings with UTF8 support, in contrast to e.g. std::basic_string<unsigned char>
      = (name === "std::string");
  
      registerType(rawType, {
        name,
        // For some method names we use string keys here since they are part of
        // the public/external API and/or used by the runtime-generated code.
        'fromWireType'(value) {
          var length = HEAPU32[((value)>>2)];
          var payload = value + 4;
  
          var str;
          if (stdStringIsUTF8) {
            var decodeStartPtr = payload;
            // Looping here to support possible embedded '0' bytes
            for (var i = 0; i <= length; ++i) {
              var currentBytePtr = payload + i;
              if (i == length || HEAPU8[currentBytePtr] == 0) {
                var maxRead = currentBytePtr - decodeStartPtr;
                var stringSegment = UTF8ToString(decodeStartPtr, maxRead);
                if (str === undefined) {
                  str = stringSegment;
                } else {
                  str += String.fromCharCode(0);
                  str += stringSegment;
                }
                decodeStartPtr = currentBytePtr + 1;
              }
            }
          } else {
            var a = new Array(length);
            for (var i = 0; i < length; ++i) {
              a[i] = String.fromCharCode(HEAPU8[payload + i]);
            }
            str = a.join('');
          }
  
          _free(value);
  
          return str;
        },
        'toWireType'(destructors, value) {
          if (value instanceof ArrayBuffer) {
            value = new Uint8Array(value);
          }
  
          var length;
          var valueIsOfTypeString = (typeof value == 'string');
  
          if (!(valueIsOfTypeString || value instanceof Uint8Array || value instanceof Uint8ClampedArray || value instanceof Int8Array)) {
            throwBindingError('Cannot pass non-string to std::string');
          }
          if (stdStringIsUTF8 && valueIsOfTypeString) {
            length = lengthBytesUTF8(value);
          } else {
            length = value.length;
          }
  
          // assumes 4-byte alignment
          var base = _malloc(4 + length + 1);
          var ptr = base + 4;
          HEAPU32[((base)>>2)] = length;
          if (stdStringIsUTF8 && valueIsOfTypeString) {
            stringToUTF8(value, ptr, length + 1);
          } else {
            if (valueIsOfTypeString) {
              for (var i = 0; i < length; ++i) {
                var charCode = value.charCodeAt(i);
                if (charCode > 255) {
                  _free(ptr);
                  throwBindingError('String has UTF-16 code units that do not fit in 8 bits');
                }
                HEAPU8[ptr + i] = charCode;
              }
            } else {
              for (var i = 0; i < length; ++i) {
                HEAPU8[ptr + i] = value[i];
              }
            }
          }
  
          if (destructors !== null) {
            destructors.push(_free, base);
          }
          return base;
        },
        'argPackAdvance': GenericWireTypeSize,
        'readValueFromPointer': readPointer,
        destructorFunction(ptr) {
          _free(ptr);
        },
      });
    };

  
  
  
  var UTF16Decoder = typeof TextDecoder != 'undefined' ? new TextDecoder('utf-16le') : undefined;;
  var UTF16ToString = (ptr, maxBytesToRead) => {
      assert(ptr % 2 == 0, 'Pointer passed to UTF16ToString must be aligned to two bytes!');
      var endPtr = ptr;
      // TextDecoder needs to know the byte length in advance, it doesn't stop on
      // null terminator by itself.
      // Also, use the length info to avoid running tiny strings through
      // TextDecoder, since .subarray() allocates garbage.
      var idx = endPtr >> 1;
      var maxIdx = idx + maxBytesToRead / 2;
      // If maxBytesToRead is not passed explicitly, it will be undefined, and this
      // will always evaluate to true. This saves on code size.
      while (!(idx >= maxIdx) && HEAPU16[idx]) ++idx;
      endPtr = idx << 1;
  
      if (endPtr - ptr > 32 && UTF16Decoder)
        return UTF16Decoder.decode(HEAPU8.subarray(ptr, endPtr));
  
      // Fallback: decode without UTF16Decoder
      var str = '';
  
      // If maxBytesToRead is not passed explicitly, it will be undefined, and the
      // for-loop's condition will always evaluate to true. The loop is then
      // terminated on the first null char.
      for (var i = 0; !(i >= maxBytesToRead / 2); ++i) {
        var codeUnit = HEAP16[(((ptr)+(i*2))>>1)];
        if (codeUnit == 0) break;
        // fromCharCode constructs a character from a UTF-16 code unit, so we can
        // pass the UTF16 string right through.
        str += String.fromCharCode(codeUnit);
      }
  
      return str;
    };
  
  var stringToUTF16 = (str, outPtr, maxBytesToWrite) => {
      assert(outPtr % 2 == 0, 'Pointer passed to stringToUTF16 must be aligned to two bytes!');
      assert(typeof maxBytesToWrite == 'number', 'stringToUTF16(str, outPtr, maxBytesToWrite) is missing the third parameter that specifies the length of the output buffer!');
      // Backwards compatibility: if max bytes is not specified, assume unsafe unbounded write is allowed.
      if (maxBytesToWrite === undefined) {
        maxBytesToWrite = 0x7FFFFFFF;
      }
      if (maxBytesToWrite < 2) return 0;
      maxBytesToWrite -= 2; // Null terminator.
      var startPtr = outPtr;
      var numCharsToWrite = (maxBytesToWrite < str.length*2) ? (maxBytesToWrite / 2) : str.length;
      for (var i = 0; i < numCharsToWrite; ++i) {
        // charCodeAt returns a UTF-16 encoded code unit, so it can be directly written to the HEAP.
        var codeUnit = str.charCodeAt(i); // possibly a lead surrogate
        HEAP16[((outPtr)>>1)] = codeUnit;
        outPtr += 2;
      }
      // Null-terminate the pointer to the HEAP.
      HEAP16[((outPtr)>>1)] = 0;
      return outPtr - startPtr;
    };
  
  var lengthBytesUTF16 = (str) => {
      return str.length*2;
    };
  
  var UTF32ToString = (ptr, maxBytesToRead) => {
      assert(ptr % 4 == 0, 'Pointer passed to UTF32ToString must be aligned to four bytes!');
      var i = 0;
  
      var str = '';
      // If maxBytesToRead is not passed explicitly, it will be undefined, and this
      // will always evaluate to true. This saves on code size.
      while (!(i >= maxBytesToRead / 4)) {
        var utf32 = HEAP32[(((ptr)+(i*4))>>2)];
        if (utf32 == 0) break;
        ++i;
        // Gotcha: fromCharCode constructs a character from a UTF-16 encoded code (pair), not from a Unicode code point! So encode the code point to UTF-16 for constructing.
        // See http://unicode.org/faq/utf_bom.html#utf16-3
        if (utf32 >= 0x10000) {
          var ch = utf32 - 0x10000;
          str += String.fromCharCode(0xD800 | (ch >> 10), 0xDC00 | (ch & 0x3FF));
        } else {
          str += String.fromCharCode(utf32);
        }
      }
      return str;
    };
  
  var stringToUTF32 = (str, outPtr, maxBytesToWrite) => {
      assert(outPtr % 4 == 0, 'Pointer passed to stringToUTF32 must be aligned to four bytes!');
      assert(typeof maxBytesToWrite == 'number', 'stringToUTF32(str, outPtr, maxBytesToWrite) is missing the third parameter that specifies the length of the output buffer!');
      // Backwards compatibility: if max bytes is not specified, assume unsafe unbounded write is allowed.
      if (maxBytesToWrite === undefined) {
        maxBytesToWrite = 0x7FFFFFFF;
      }
      if (maxBytesToWrite < 4) return 0;
      var startPtr = outPtr;
      var endPtr = startPtr + maxBytesToWrite - 4;
      for (var i = 0; i < str.length; ++i) {
        // Gotcha: charCodeAt returns a 16-bit word that is a UTF-16 encoded code unit, not a Unicode code point of the character! We must decode the string to UTF-32 to the heap.
        // See http://unicode.org/faq/utf_bom.html#utf16-3
        var codeUnit = str.charCodeAt(i); // possibly a lead surrogate
        if (codeUnit >= 0xD800 && codeUnit <= 0xDFFF) {
          var trailSurrogate = str.charCodeAt(++i);
          codeUnit = 0x10000 + ((codeUnit & 0x3FF) << 10) | (trailSurrogate & 0x3FF);
        }
        HEAP32[((outPtr)>>2)] = codeUnit;
        outPtr += 4;
        if (outPtr + 4 > endPtr) break;
      }
      // Null-terminate the pointer to the HEAP.
      HEAP32[((outPtr)>>2)] = 0;
      return outPtr - startPtr;
    };
  
  var lengthBytesUTF32 = (str) => {
      var len = 0;
      for (var i = 0; i < str.length; ++i) {
        // Gotcha: charCodeAt returns a 16-bit word that is a UTF-16 encoded code unit, not a Unicode code point of the character! We must decode the string to UTF-32 to the heap.
        // See http://unicode.org/faq/utf_bom.html#utf16-3
        var codeUnit = str.charCodeAt(i);
        if (codeUnit >= 0xD800 && codeUnit <= 0xDFFF) ++i; // possibly a lead surrogate, so skip over the tail surrogate.
        len += 4;
      }
  
      return len;
    };
  var __embind_register_std_wstring = (rawType, charSize, name) => {
      name = readLatin1String(name);
      var decodeString, encodeString, getHeap, lengthBytesUTF, shift;
      if (charSize === 2) {
        decodeString = UTF16ToString;
        encodeString = stringToUTF16;
        lengthBytesUTF = lengthBytesUTF16;
        getHeap = () => HEAPU16;
        shift = 1;
      } else if (charSize === 4) {
        decodeString = UTF32ToString;
        encodeString = stringToUTF32;
        lengthBytesUTF = lengthBytesUTF32;
        getHeap = () => HEAPU32;
        shift = 2;
      }
      registerType(rawType, {
        name,
        'fromWireType': (value) => {
          // Code mostly taken from _embind_register_std_string fromWireType
          var length = HEAPU32[((value)>>2)];
          var HEAP = getHeap();
          var str;
  
          var decodeStartPtr = value + 4;
          // Looping here to support possible embedded '0' bytes
          for (var i = 0; i <= length; ++i) {
            var currentBytePtr = value + 4 + i * charSize;
            if (i == length || HEAP[currentBytePtr >> shift] == 0) {
              var maxReadBytes = currentBytePtr - decodeStartPtr;
              var stringSegment = decodeString(decodeStartPtr, maxReadBytes);
              if (str === undefined) {
                str = stringSegment;
              } else {
                str += String.fromCharCode(0);
                str += stringSegment;
              }
              decodeStartPtr = currentBytePtr + charSize;
            }
          }
  
          _free(value);
  
          return str;
        },
        'toWireType': (destructors, value) => {
          if (!(typeof value == 'string')) {
            throwBindingError(`Cannot pass non-string to C++ string type ${name}`);
          }
  
          // assumes 4-byte alignment
          var length = lengthBytesUTF(value);
          var ptr = _malloc(4 + length + charSize);
          HEAPU32[ptr >> 2] = length >> shift;
  
          encodeString(value, ptr + 4, length + charSize);
  
          if (destructors !== null) {
            destructors.push(_free, ptr);
          }
          return ptr;
        },
        'argPackAdvance': GenericWireTypeSize,
        'readValueFromPointer': simpleReadValueFromPointer,
        destructorFunction(ptr) {
          _free(ptr);
        }
      });
    };

  
  var __embind_register_void = (rawType, name) => {
      name = readLatin1String(name);
      registerType(rawType, {
        isVoid: true, // void return values can be optimized out sometimes
        name,
        'argPackAdvance': 0,
        'fromWireType': () => undefined,
        // TODO: assert if anything else is given?
        'toWireType': (destructors, o) => undefined,
      });
    };

  var _abort = () => {
      abort('native code called abort()');
    };

  var _emscripten_memcpy_js = (dest, src, num) => HEAPU8.copyWithin(dest, src, src + num);

  var getHeapMax = () =>
      HEAPU8.length;
  
  var abortOnCannotGrowMemory = (requestedSize) => {
      abort(`Cannot enlarge memory arrays to size ${requestedSize} bytes (OOM). Either (1) compile with -sINITIAL_MEMORY=X with X higher than the current value ${HEAP8.length}, (2) compile with -sALLOW_MEMORY_GROWTH which allows increasing the size at runtime, or (3) if you want malloc to return NULL (0) instead of this abort, compile with -sABORTING_MALLOC=0`);
    };
  var _emscripten_resize_heap = (requestedSize) => {
      var oldSize = HEAPU8.length;
      // With CAN_ADDRESS_2GB or MEMORY64, pointers are already unsigned.
      requestedSize >>>= 0;
      abortOnCannotGrowMemory(requestedSize);
    };

  var SYSCALLS = {
  varargs:undefined,
  get() {
        assert(SYSCALLS.varargs != undefined);
        // the `+` prepended here is necessary to convince the JSCompiler that varargs is indeed a number.
        var ret = HEAP32[((+SYSCALLS.varargs)>>2)];
        SYSCALLS.varargs += 4;
        return ret;
      },
  getp() { return SYSCALLS.get() },
  getStr(ptr) {
        var ret = UTF8ToString(ptr);
        return ret;
      },
  };
  var _fd_close = (fd) => {
      abort('fd_close called without SYSCALLS_REQUIRE_FILESYSTEM');
    };

  
  var convertI32PairToI53Checked = (lo, hi) => {
      assert(lo == (lo >>> 0) || lo == (lo|0)); // lo should either be a i32 or a u32
      assert(hi === (hi|0));                    // hi should be a i32
      return ((hi + 0x200000) >>> 0 < 0x400001 - !!lo) ? (lo >>> 0) + hi * 4294967296 : NaN;
    };
  function _fd_seek(fd,offset_low, offset_high,whence,newOffset) {
    var offset = convertI32PairToI53Checked(offset_low, offset_high);;
  
    
      return 70;
    ;
  }

  var printCharBuffers = [null,[],[]];
  
  var printChar = (stream, curr) => {
      var buffer = printCharBuffers[stream];
      assert(buffer);
      if (curr === 0 || curr === 10) {
        (stream === 1 ? out : err)(UTF8ArrayToString(buffer, 0));
        buffer.length = 0;
      } else {
        buffer.push(curr);
      }
    };
  
  var flush_NO_FILESYSTEM = () => {
      // flush anything remaining in the buffers during shutdown
      _fflush(0);
      if (printCharBuffers[1].length) printChar(1, 10);
      if (printCharBuffers[2].length) printChar(2, 10);
    };
  
  
  var _fd_write = (fd, iov, iovcnt, pnum) => {
      // hack to support printf in SYSCALLS_REQUIRE_FILESYSTEM=0
      var num = 0;
      for (var i = 0; i < iovcnt; i++) {
        var ptr = HEAPU32[((iov)>>2)];
        var len = HEAPU32[(((iov)+(4))>>2)];
        iov += 8;
        for (var j = 0; j < len; j++) {
          printChar(fd, HEAPU8[ptr+j]);
        }
        num += len;
      }
      HEAPU32[((pnum)>>2)] = num;
      return 0;
    };
embind_init_charCodes();
BindingError = Module['BindingError'] = class BindingError extends Error { constructor(message) { super(message); this.name = 'BindingError'; }};
InternalError = Module['InternalError'] = class InternalError extends Error { constructor(message) { super(message); this.name = 'InternalError'; }};
handleAllocatorInit();
init_emval();;
UnboundTypeError = Module['UnboundTypeError'] = extendError(Error, 'UnboundTypeError');;
function checkIncomingModuleAPI() {
  ignoredModuleProp('fetchSettings');
}
var wasmImports = {
  /** @export */
  __cxa_throw: ___cxa_throw,
  /** @export */
  _embind_register_bigint: __embind_register_bigint,
  /** @export */
  _embind_register_bool: __embind_register_bool,
  /** @export */
  _embind_register_emval: __embind_register_emval,
  /** @export */
  _embind_register_float: __embind_register_float,
  /** @export */
  _embind_register_function: __embind_register_function,
  /** @export */
  _embind_register_integer: __embind_register_integer,
  /** @export */
  _embind_register_memory_view: __embind_register_memory_view,
  /** @export */
  _embind_register_std_string: __embind_register_std_string,
  /** @export */
  _embind_register_std_wstring: __embind_register_std_wstring,
  /** @export */
  _embind_register_void: __embind_register_void,
  /** @export */
  abort: _abort,
  /** @export */
  emscripten_memcpy_js: _emscripten_memcpy_js,
  /** @export */
  emscripten_resize_heap: _emscripten_resize_heap,
  /** @export */
  fd_close: _fd_close,
  /** @export */
  fd_seek: _fd_seek,
  /** @export */
  fd_write: _fd_write
};
var wasmExports = createWasm();
var ___wasm_call_ctors = createExportWrapper('__wasm_call_ctors');
var _malloc = createExportWrapper('malloc');
var ___getTypeName = createExportWrapper('__getTypeName');
var ___errno_location = createExportWrapper('__errno_location');
var _fflush = Module['_fflush'] = createExportWrapper('fflush');
var _free = createExportWrapper('free');
var _emscripten_stack_init = () => (_emscripten_stack_init = wasmExports['emscripten_stack_init'])();
var _emscripten_stack_get_free = () => (_emscripten_stack_get_free = wasmExports['emscripten_stack_get_free'])();
var _emscripten_stack_get_base = () => (_emscripten_stack_get_base = wasmExports['emscripten_stack_get_base'])();
var _emscripten_stack_get_end = () => (_emscripten_stack_get_end = wasmExports['emscripten_stack_get_end'])();
var stackSave = createExportWrapper('stackSave');
var stackRestore = createExportWrapper('stackRestore');
var stackAlloc = createExportWrapper('stackAlloc');
var _emscripten_stack_get_current = () => (_emscripten_stack_get_current = wasmExports['emscripten_stack_get_current'])();
var ___cxa_is_pointer_type = createExportWrapper('__cxa_is_pointer_type');
var dynCall_jiji = Module['dynCall_jiji'] = createExportWrapper('dynCall_jiji');


// include: postamble.js
// === Auto-generated postamble setup entry stuff ===

var missingLibrarySymbols = [
  'writeI53ToI64',
  'writeI53ToI64Clamped',
  'writeI53ToI64Signaling',
  'writeI53ToU64Clamped',
  'writeI53ToU64Signaling',
  'readI53FromI64',
  'readI53FromU64',
  'convertI32PairToI53',
  'convertU32PairToI53',
  'zeroMemory',
  'exitJS',
  'growMemory',
  'isLeapYear',
  'ydayFromDate',
  'arraySum',
  'addDays',
  'setErrNo',
  'inetPton4',
  'inetNtop4',
  'inetPton6',
  'inetNtop6',
  'readSockaddr',
  'writeSockaddr',
  'getHostByName',
  'initRandomFill',
  'randomFill',
  'getCallstack',
  'emscriptenLog',
  'convertPCtoSourceLocation',
  'readEmAsmArgs',
  'jstoi_q',
  'jstoi_s',
  'getExecutableName',
  'listenOnce',
  'autoResumeAudioContext',
  'handleException',
  'keepRuntimeAlive',
  'runtimeKeepalivePush',
  'runtimeKeepalivePop',
  'callUserCallback',
  'maybeExit',
  'asmjsMangle',
  'asyncLoad',
  'alignMemory',
  'mmapAlloc',
  'getNativeTypeSize',
  'STACK_SIZE',
  'STACK_ALIGN',
  'POINTER_SIZE',
  'ASSERTIONS',
  'getCFunc',
  'ccall',
  'cwrap',
  'uleb128Encode',
  'sigToWasmTypes',
  'generateFuncType',
  'convertJsFunctionToWasm',
  'getEmptyTableSlot',
  'updateTableMap',
  'getFunctionAddress',
  'addFunction',
  'removeFunction',
  'reallyNegative',
  'unSign',
  'strLen',
  'reSign',
  'formatString',
  'intArrayFromString',
  'intArrayToString',
  'AsciiToString',
  'stringToAscii',
  'stringToNewUTF8',
  'stringToUTF8OnStack',
  'writeArrayToMemory',
  'registerKeyEventCallback',
  'maybeCStringToJsString',
  'findEventTarget',
  'findCanvasEventTarget',
  'getBoundingClientRect',
  'fillMouseEventData',
  'registerMouseEventCallback',
  'registerWheelEventCallback',
  'registerUiEventCallback',
  'registerFocusEventCallback',
  'fillDeviceOrientationEventData',
  'registerDeviceOrientationEventCallback',
  'fillDeviceMotionEventData',
  'registerDeviceMotionEventCallback',
  'screenOrientation',
  'fillOrientationChangeEventData',
  'registerOrientationChangeEventCallback',
  'fillFullscreenChangeEventData',
  'registerFullscreenChangeEventCallback',
  'JSEvents_requestFullscreen',
  'JSEvents_resizeCanvasForFullscreen',
  'registerRestoreOldStyle',
  'hideEverythingExceptGivenElement',
  'restoreHiddenElements',
  'setLetterbox',
  'softFullscreenResizeWebGLRenderTarget',
  'doRequestFullscreen',
  'fillPointerlockChangeEventData',
  'registerPointerlockChangeEventCallback',
  'registerPointerlockErrorEventCallback',
  'requestPointerLock',
  'fillVisibilityChangeEventData',
  'registerVisibilityChangeEventCallback',
  'registerTouchEventCallback',
  'fillGamepadEventData',
  'registerGamepadEventCallback',
  'registerBeforeUnloadEventCallback',
  'fillBatteryEventData',
  'battery',
  'registerBatteryEventCallback',
  'setCanvasElementSize',
  'getCanvasElementSize',
  'demangle',
  'demangleAll',
  'jsStackTrace',
  'stackTrace',
  'getEnvStrings',
  'checkWasiClock',
  'wasiRightsToMuslOFlags',
  'wasiOFlagsToMuslOFlags',
  'createDyncallWrapper',
  'safeSetTimeout',
  'setImmediateWrapped',
  'clearImmediateWrapped',
  'polyfillSetImmediate',
  'getPromise',
  'makePromise',
  'idsToPromises',
  'makePromiseCallback',
  'findMatchingCatch',
  'setMainLoop',
  'getSocketFromFD',
  'getSocketAddress',
  'FS_createPreloadedFile',
  'FS_modeStringToFlags',
  'FS_getMode',
  'FS_stdin_getChar',
  'FS_createDataFile',
  'FS_unlink',
  'FS_mkdirTree',
  '_setNetworkCallback',
  'heapObjectForWebGLType',
  'heapAccessShiftForWebGLHeap',
  'webgl_enable_ANGLE_instanced_arrays',
  'webgl_enable_OES_vertex_array_object',
  'webgl_enable_WEBGL_draw_buffers',
  'webgl_enable_WEBGL_multi_draw',
  'emscriptenWebGLGet',
  'computeUnpackAlignedImageSize',
  'colorChannelsInGlTextureFormat',
  'emscriptenWebGLGetTexPixelData',
  '__glGenObject',
  'emscriptenWebGLGetUniform',
  'webglGetUniformLocation',
  'webglPrepareUniformLocationsBeforeFirstUse',
  'webglGetLeftBracePos',
  'emscriptenWebGLGetVertexAttrib',
  '__glGetActiveAttribOrUniform',
  'writeGLArray',
  'registerWebGlEventCallback',
  'runAndAbortIfError',
  'SDL_unicode',
  'SDL_ttfContext',
  'SDL_audio',
  'ALLOC_NORMAL',
  'ALLOC_STACK',
  'allocate',
  'writeStringToMemory',
  'writeAsciiToMemory',
  'getFunctionArgsName',
  'requireRegisteredType',
  'init_embind',
  'getBasestPointer',
  'registerInheritedInstance',
  'unregisterInheritedInstance',
  'getInheritedInstance',
  'getInheritedInstanceCount',
  'getLiveInheritedInstances',
  'enumReadValueFromPointer',
  'genericPointerToWireType',
  'constNoSmartPtrRawPointerToWireType',
  'nonConstNoSmartPtrRawPointerToWireType',
  'init_RegisteredPointer',
  'RegisteredPointer',
  'RegisteredPointer_fromWireType',
  'runDestructor',
  'releaseClassHandle',
  'detachFinalizer',
  'attachFinalizer',
  'makeClassHandle',
  'init_ClassHandle',
  'ClassHandle',
  'throwInstanceAlreadyDeleted',
  'flushPendingDeletes',
  'setDelayFunction',
  'RegisteredClass',
  'shallowCopyInternalPointer',
  'downcastPointer',
  'upcastPointer',
  'validateThis',
  'char_0',
  'char_9',
  'makeLegalFunctionName',
  'getStringOrSymbol',
  'emval_get_global',
  'emval_returnValue',
  'emval_lookupTypes',
  'emval_addMethodCaller',
];
missingLibrarySymbols.forEach(missingLibrarySymbol)

var unexportedSymbols = [
  'run',
  'addOnPreRun',
  'addOnInit',
  'addOnPreMain',
  'addOnExit',
  'addOnPostRun',
  'addRunDependency',
  'removeRunDependency',
  'FS_createFolder',
  'FS_createPath',
  'FS_createLazyFile',
  'FS_createLink',
  'FS_createDevice',
  'FS_readFile',
  'out',
  'err',
  'callMain',
  'abort',
  'wasmMemory',
  'wasmExports',
  'stackAlloc',
  'stackSave',
  'stackRestore',
  'getTempRet0',
  'setTempRet0',
  'writeStackCookie',
  'checkStackCookie',
  'intArrayFromBase64',
  'tryParseAsDataURI',
  'convertI32PairToI53Checked',
  'ptrToString',
  'getHeapMax',
  'abortOnCannotGrowMemory',
  'ENV',
  'MONTH_DAYS_REGULAR',
  'MONTH_DAYS_LEAP',
  'MONTH_DAYS_REGULAR_CUMULATIVE',
  'MONTH_DAYS_LEAP_CUMULATIVE',
  'ERRNO_CODES',
  'ERRNO_MESSAGES',
  'DNS',
  'Protocols',
  'Sockets',
  'timers',
  'warnOnce',
  'UNWIND_CACHE',
  'readEmAsmArgsArray',
  'dynCallLegacy',
  'getDynCaller',
  'dynCall',
  'handleAllocatorInit',
  'HandleAllocator',
  'wasmTable',
  'noExitRuntime',
  'freeTableIndexes',
  'functionsInTableMap',
  'setValue',
  'getValue',
  'PATH',
  'PATH_FS',
  'UTF8Decoder',
  'UTF8ArrayToString',
  'UTF8ToString',
  'stringToUTF8Array',
  'stringToUTF8',
  'lengthBytesUTF8',
  'UTF16Decoder',
  'UTF16ToString',
  'stringToUTF16',
  'lengthBytesUTF16',
  'UTF32ToString',
  'stringToUTF32',
  'lengthBytesUTF32',
  'JSEvents',
  'specialHTMLTargets',
  'currentFullscreenStrategy',
  'restoreOldWindowedStyle',
  'ExitStatus',
  'flush_NO_FILESYSTEM',
  'promiseMap',
  'uncaughtExceptionCount',
  'exceptionLast',
  'exceptionCaught',
  'ExceptionInfo',
  'Browser',
  'wget',
  'SYSCALLS',
  'preloadPlugins',
  'FS_stdin_getChar_buffer',
  'FS',
  'MEMFS',
  'TTY',
  'PIPEFS',
  'SOCKFS',
  'tempFixedLengthArray',
  'miniTempWebGLFloatBuffers',
  'miniTempWebGLIntBuffers',
  'GL',
  'emscripten_webgl_power_preferences',
  'AL',
  'GLUT',
  'EGL',
  'GLEW',
  'IDBStore',
  'SDL',
  'SDL_gfx',
  'allocateUTF8',
  'allocateUTF8OnStack',
  'InternalError',
  'BindingError',
  'throwInternalError',
  'throwBindingError',
  'registeredTypes',
  'awaitingDependencies',
  'typeDependencies',
  'tupleRegistrations',
  'structRegistrations',
  'sharedRegisterType',
  'whenDependentTypesAreResolved',
  'embind_charCodes',
  'embind_init_charCodes',
  'readLatin1String',
  'getTypeName',
  'getFunctionName',
  'heap32VectorToArray',
  'UnboundTypeError',
  'PureVirtualError',
  'GenericWireTypeSize',
  'throwUnboundTypeError',
  'ensureOverloadTable',
  'exposePublicSymbol',
  'replacePublicSymbol',
  'extendError',
  'createNamedFunction',
  'embindRepr',
  'registeredInstances',
  'registeredPointers',
  'registerType',
  'integerReadValueFromPointer',
  'floatReadValueFromPointer',
  'simpleReadValueFromPointer',
  'readPointer',
  'runDestructors',
  'newFunc',
  'craftInvokerFunction',
  'embind__requireFunction',
  'finalizationRegistry',
  'detachFinalizer_deps',
  'deletionQueue',
  'delayFunction',
  'emval_handles',
  'emval_symbols',
  'init_emval',
  'count_emval_handles',
  'Emval',
  'emval_methodCallers',
  'reflectConstruct',
];
unexportedSymbols.forEach(unexportedRuntimeSymbol);



var calledRun;

dependenciesFulfilled = function runCaller() {
  // If run has never been called, and we should call run (INVOKE_RUN is true, and Module.noInitialRun is not false)
  if (!calledRun) run();
  if (!calledRun) dependenciesFulfilled = runCaller; // try this again later, after new deps are fulfilled
};

function stackCheckInit() {
  // This is normally called automatically during __wasm_call_ctors but need to
  // get these values before even running any of the ctors so we call it redundantly
  // here.
  _emscripten_stack_init();
  // TODO(sbc): Move writeStackCookie to native to to avoid this.
  writeStackCookie();
}

function run() {

  if (runDependencies > 0) {
    return;
  }

    stackCheckInit();

  preRun();

  // a preRun added a dependency, run will be called later
  if (runDependencies > 0) {
    return;
  }

  function doRun() {
    // run may have just been called through dependencies being fulfilled just in this very frame,
    // or while the async setStatus time below was happening
    if (calledRun) return;
    calledRun = true;
    Module['calledRun'] = true;

    if (ABORT) return;

    initRuntime();

    readyPromiseResolve(Module);
    if (Module['onRuntimeInitialized']) Module['onRuntimeInitialized']();

    assert(!Module['_main'], 'compiled without a main, but one is present. if you added it from JS, use Module["onRuntimeInitialized"]');

    postRun();
  }

  if (Module['setStatus']) {
    Module['setStatus']('Running...');
    setTimeout(function() {
      setTimeout(function() {
        Module['setStatus']('');
      }, 1);
      doRun();
    }, 1);
  } else
  {
    doRun();
  }
  checkStackCookie();
}

function checkUnflushedContent() {
  // Compiler settings do not allow exiting the runtime, so flushing
  // the streams is not possible. but in ASSERTIONS mode we check
  // if there was something to flush, and if so tell the user they
  // should request that the runtime be exitable.
  // Normally we would not even include flush() at all, but in ASSERTIONS
  // builds we do so just for this check, and here we see if there is any
  // content to flush, that is, we check if there would have been
  // something a non-ASSERTIONS build would have not seen.
  // How we flush the streams depends on whether we are in SYSCALLS_REQUIRE_FILESYSTEM=0
  // mode (which has its own special function for this; otherwise, all
  // the code is inside libc)
  var oldOut = out;
  var oldErr = err;
  var has = false;
  out = err = (x) => {
    has = true;
  }
  try { // it doesn't matter if it fails
    flush_NO_FILESYSTEM();
  } catch(e) {}
  out = oldOut;
  err = oldErr;
  if (has) {
    warnOnce('stdio streams had content in them that was not flushed. you should set EXIT_RUNTIME to 1 (see the Emscripten FAQ), or make sure to emit a newline when you printf etc.');
    warnOnce('(this may also be due to not including full filesystem support - try building with -sFORCE_FILESYSTEM)');
  }
}

if (Module['preInit']) {
  if (typeof Module['preInit'] == 'function') Module['preInit'] = [Module['preInit']];
  while (Module['preInit'].length > 0) {
    Module['preInit'].pop()();
  }
}

run();


// end include: postamble.js


  return moduleArg.ready
}
);
})();
;
if (typeof exports === 'object' && typeof module === 'object')
  module.exports = Module;
else if (typeof define === 'function' && define['amd'])
  define([], () => Module);
