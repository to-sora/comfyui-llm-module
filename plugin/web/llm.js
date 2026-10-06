import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
  name: "comfyui.llm.response",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "LLMChat") return;
    const executed = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (output) {
      executed?.apply(this, arguments);
      const result = JSON.parse(output.text[0]).choices[0].message;
      let widget = this.widgets?.find((item) => item.name === "response");
      if (!widget) {
        widget = ComfyWidgets.STRING(this, "response", ["STRING", { multiline: true }], app).widget;
        widget.options.serialize = false;
        widget.inputEl.readOnly = true;
      }
      widget.value = result.tool_calls
        ? result.tool_calls.map(({ function: fn }) =>
            `${fn.name}(${JSON.stringify(JSON.parse(fn.arguments), null, 2)})`).join("\n\n")
        : result.content || "";
      widget.computeSize = (width) => [width, Math.min(240,
        Math.max(100, (widget.value.split("\n").length + 1) * 18))];
      const size = this.computeSize();
      this.setSize([Math.max(420, this.size[0], size[0]),
        Math.max(560, this.size[1], size[1])]);
      this.setDirtyCanvas(true, true);
    };
  },
});
