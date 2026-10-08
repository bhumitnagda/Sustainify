(function() {
  var loaderElements = document.querySelectorAll("covet-widget-loader").length

  if (loaderElements === 0) {
    var scriptElmModule = document.createElement("script")
    scriptElmModule.src = "https://cdn.jsdelivr.net/npm/@covet-pics/covet-pics-widget@latest/dist/covet-pics-widget/covet-pics-widget.esm.js"
    scriptElmModule.setAttribute("type", "module")
    document.querySelector("head").appendChild(scriptElmModule)

    var scriptElmPolyfill = document.createElement("script")
    scriptElmPolyfill.src = "https://cdn.jsdelivr.net/npm/@covet-pics/covet-pics-widget@latest/dist/covet-pics-widget/covet-pics-widget.js"
    scriptElmPolyfill.setAttribute("nomodule", "")
    document.querySelector("head").appendChild(scriptElmPolyfill)
  }
})()
