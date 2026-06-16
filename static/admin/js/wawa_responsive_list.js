// Universal responsive changelist support.
//
// Copies each column's header text onto its data cells as a `data-label`
// attribute, so the mobile stacked-card CSS can render every cell as a
// "Column: value" line. This is model-agnostic — it works for any changelist,
// current or future, with no per-model configuration.
(function () {
  function labelCells() {
    document.querySelectorAll("#result_list").forEach(function (table) {
      var headers = Array.prototype.map.call(
        table.querySelectorAll("thead th"),
        function (th) { return th.textContent.trim(); }
      );
      table.querySelectorAll("tbody tr").forEach(function (row) {
        Array.prototype.forEach.call(row.children, function (cell, i) {
          var label = headers[i];
          if (label) {
            cell.setAttribute("data-label", label);
          }
        });
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", labelCells);
  } else {
    labelCells();
  }
})();
