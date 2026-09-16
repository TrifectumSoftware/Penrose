/* ============================================================
   Voronoi desktop background (WebGL, smooth drift).
   True per-frame site drift at 60fps for buttery motion, but
   rendered at 1/8 resolution and upscaled smoothly: soft
   organic cells at a fraction of the fragment cost, so zooming
   and scrolling stay fast.

   Site positions are computed once per frame on the CPU and
   passed as uniforms — the fragment shader does no trig/hash.
   ============================================================ */
(function () {
  var canvas = document.getElementById("voronoi-bg");
  if (!canvas) return;

  var gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
  if (!gl) return;

  var N = 22;
  var SCALE = 8;

  var cfg = window.WIKI_CONFIG || {};
  var LIGHT = {
    base: cfg.voronoiLightBase || [0, 128, 128],
    cell: cfg.voronoiLightCell || [16, 146, 146]
  };
  var DARK = {
    base: cfg.voronoiDarkBase || [4, 15, 15],
    cell: cfg.voronoiDarkCell || [8, 26, 26]
  };

  var VERT = [
    "attribute vec2 a_pos;",
    "void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }"
  ].join("\n");

  var FRAG = [
    "precision mediump float;",
    "uniform vec2 u_resolution;",
    "uniform vec2 u_sites[" + N + "];",
    "uniform vec3 u_base;",
    "uniform vec3 u_cell;",
    "",
    "void main() {",
    "  vec2 uv = gl_FragCoord.xy / u_resolution.xy;",
    "  float aspect = u_resolution.x / u_resolution.y;",
    "  vec2 p = vec2(uv.x * aspect, uv.y);",
    "",
    "  float d1 = 1e10;",
    "  float d2 = 1e10;",
    "  for (int i = 0; i < " + N + "; i++) {",
    "    vec2 site = vec2(u_sites[i].x * aspect, u_sites[i].y);",
    "    vec2 d = p - site;",
    "    float dist = dot(d, d);",
    "    if (dist < d1) { d2 = d1; d1 = dist; }",
    "    else if (dist < d2) { d2 = dist; }",
    "  }",
    "",
    "  float e = sqrt(d2) - sqrt(d1);",
    "  float edge = smoothstep(0.0, 0.012, e);",
    "  gl_FragColor = vec4(mix(u_base, u_cell, edge), 1.0);",
    "}"
  ].join("\n");

  function compile(type, src) {
    var sh = gl.createShader(type);
    gl.shaderSource(sh, src);
    gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
      console.error(gl.getShaderInfoLog(sh));
      return null;
    }
    return sh;
  }

  var vs = compile(gl.VERTEX_SHADER, VERT);
  var fs = compile(gl.FRAGMENT_SHADER, FRAG);
  if (!vs || !fs) return;

  var prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
  gl.useProgram(prog);

  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

  var aPos = gl.getAttribLocation(prog, "a_pos");
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  var uRes = gl.getUniformLocation(prog, "u_resolution");
  var uSites = gl.getUniformLocation(prog, "u_sites");
  var uBase = gl.getUniformLocation(prog, "u_base");
  var uCell = gl.getUniformLocation(prog, "u_cell");

  var base = new Float32Array(N * 2);
  for (var i = 0; i < N; i++) {
    base[i * 2] = 0.15 + 0.7 * Math.random();
    base[i * 2 + 1] = 0.15 + 0.7 * Math.random();
  }
  var sites = new Float32Array(N * 2);
  var currentDark = null;

  function applyTheme() {
    var dark = document.documentElement.classList.contains("theme-dark");
    if (dark === currentDark) return;
    currentDark = dark;
    var c = dark ? DARK : LIGHT;
    gl.uniform3f(uBase, c.base[0] / 255, c.base[1] / 255, c.base[2] / 255);
    gl.uniform3f(uCell, c.cell[0] / 255, c.cell[1] / 255, c.cell[2] / 255);
  }

  function resize() {
    var w = Math.max(1, Math.round(canvas.clientWidth / SCALE));
    var h = Math.max(1, Math.round(canvas.clientHeight / SCALE));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
    }
  }

  function draw(t) {
    resize();
    applyTheme();
    var time = t / 1000;
    for (var i = 0; i < N; i++) {
      sites[i * 2] = base[i * 2] + 0.08 * Math.sin(time * 0.25 + i * 1.31);
      sites[i * 2 + 1] = base[i * 2 + 1] + 0.08 * Math.cos(time * 0.21 + i * 2.17);
    }
    gl.uniform2fv(uSites, sites);
    gl.uniform2f(uRes, canvas.width, canvas.height);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  window.addEventListener("resize", resize);
  resize();

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduced) {
    draw(0);
    var mo = new MutationObserver(function () { draw(0); });
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
  } else {
    function frame(t) {
      draw(t);
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
})();
