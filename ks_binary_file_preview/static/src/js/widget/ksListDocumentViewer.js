odoo.define("ks_curved_backend_theme.KsListDocumentViewer", function (require) {
  "use strict";

  var core = require("web.core");
  var Widget = require("web.Widget");

  var QWeb = core.qweb;

  var KsListDocumentViewer = Widget.extend({
    template: "ks_curved_backend_theme.KsListDocumentViewer",
    events: {
      "click .o_viewer_img": "ksOnImageClicked",
      "click .o_download_btn": "ksOnDownload",
      "click .o_viewer_video": "ksOnVideoController",
      "click .o_zoom_reset": "ksPreviewZoomReset",
      "click .o_rotate": "ksRotatePreview",
      "click .o_zoom_in": "ksPreviewZoomIn",
      "click .o_zoom_out": "_ksZoomOutPreview",
      "click .o_close_btn": "destroy",
      "click .o_print_btn": "_ksOnPrintPreview",
      "DOMMouseScroll .o_viewer_content": "ksOnScrollPreview",
      "mousewheel .o_viewer_content": "ksOnScrollPreview",
      keyup: "ksOnKeyUp",
    },

    /**
     * Initialize list document viewer.
     */
    init: function (parent, ks_attachments, ks_activeAttachmentID) {
      this._super.apply(this, arguments);
      this.ks_attachment = _.filter(ks_attachments, function (ks_attachment) {
        if (ks_attachment.type === "url")
          var ks_match = ks_attachment.url.match("(.png|.gif|youtu|.jpg)");
        else
          var ks_match = ks_attachment.mimetype.match(
            "(image|video|text|application/pdf)"
          );

        if (ks_match) {
          ks_attachment.fileType = ks_match[1];
          if (ks_match[1] === "youtu") {
            var ks_youtube_arr = ks_attachment.url.split("/");
            var youtube_token = ks_youtube_arr[ks_youtube_arr.length - 1];
            if (youtube_token.indexOf("watch") !== -1) {
              youtube_token = youtube_token.split("v=")[1];
              var amp = youtube_token.indexOf("&");
              if (amp !== -1) {
                youtube_token = youtube_token.substring(0, amp);
              }
            }
            ks_attachment.youtube = youtube_token;
          }
          if (ks_match[1].match("(.jpg|.png|.gif)")) {
            ks_attachment.fileType = "image";
          }
          return true;
        }
      });
      this.ks_activeAttachment = _.findWhere(ks_attachments, {
        id: ks_activeAttachmentID,
      });
      this.modelName = "ir.attachment";
      this.ksPreviewReset();
    },

    start: function () {
      this.$el.modal("show");
      this.$el.on("hidden.bs.modal", _.bind(this.ksOnDestroy, this));
      this.$(".o_viewer_img").on("load", _.bind(this.ksOnImageLoaded, this));
      this.$('[data-toggle="tooltip"]').tooltip({ delay: 0 });
      return this._super.apply(this, arguments);
    },

    destroy: function () {
      // Hide and remove modal.
      this.$el.modal("hide");
      this.$el.remove();
      // If preview is already destroyed.
      if (this.isDestroyed()) {
        return;
      }
      this._super.apply(this, arguments);
    },

    ksPreviewReset: function () {
      this.scale = 1;
      this.dragStartX = this.dragstopX = 0;
      this.dragStartY = this.dragstopY = 0;
    },

    ksPreviewGetTransform: function (scale, angle) {
      return (
        "scale3d(" + scale + ", " + scale + ", 1) rotate(" + angle + "deg)"
      );
    },

    ksPreviewRotate: function (angle) {
      this.ksPreviewReset();
      var new_angle = (this.angle || 0) + angle;
      this.$(".o_viewer_img").css(
        "transform",
        this.ksPreviewGetTransform(this.scale, new_angle)
      );
      this.$(".o_viewer_img").css(
        "max-width",
        new_angle % 180 !== 0 ? $(document).height() : "100%"
      );
      this.$(".o_viewer_img").css(
        "max-height",
        new_angle % 180 !== 0 ? $(document).width() : "100%"
      );
      this.angle = new_angle;
    },

    ksPreviewZoom: function (scale) {
      if (scale > 0.5) {
        this.$(".o_viewer_img").css(
          "transform",
          this.ksPreviewGetTransform(scale, this.angle || 0)
        );
        this.scale = scale;
      }
      this.$(".o_zoom_reset")
        .add(".o_zoom_out")
        .toggleClass("disabled", scale === 1);
    },

    ksOnDestroy: function () {
      this.destroy();
    },

    /**
     * Handle download button.
     */
    ksOnDownload: function (ev) {
      ev.preventDefault();
      window.location =
        "/web/content/" +
        this.modelName +
        "/" +
        this.ks_activeAttachment.id +
        "/" +
        "datas" +
        "?download=true";
    },

    /**
     * Handle print action.
     */
    _ksOnPrintPreview: function (ev) {
      ev.preventDefault();
      var ks_src = this.$(".o_viewer_img").prop("src");
      var script = QWeb.render("im_livechat.legacy.mail.PrintImage", {
        src: ks_src,
      });
      var printWindow = window.open("about:blank", "_new");
      printWindow.document.open();
      printWindow.document.write(script);
      printWindow.document.close();
    },

    /**
     * Prevent image clicked.
     */
    ksOnImageClicked: function (ev) {
      ev.stopPropagation();
    },

    /**
     * Hide loader when after the image load.
     */
    ksOnImageLoaded: function () {
      this.$(".o_loading_img").hide();
    },

    /**
     * Handle mouse zoom.
     *
     */
    ksOnScrollPreview: function (ev) {
      var scale;
      if (ev.originalEvent.wheelDelta > 0 || ev.originalEvent.detail < 0) {
        scale = this.scale + 0.1;
        this.ksPreviewZoom(scale);
      } else {
        scale = this.scale - 0.1;
        this.ksPreviewZoom(scale);
      }
    },

    /**
     * Control media video.
     */
    ksOnVideoController: function (ev) {
      ev.stopPropagation();
      var ksVideoElement = ev.target;
      if (ksVideoElement.paused) {
        ksVideoElement.play();
      } else {
        ksVideoElement.pause();
      }
    },

    /**
     * Right rotate.
     */
    ksRotatePreview: function (ev) {
      ev.preventDefault();
      this.ksPreviewRotate(90);
    },

    /**
     * Reset preview content.
     */
    ksPreviewZoomReset: function (ev) {
      ev.preventDefault();
      this.$(".o_viewer_zoomer").css("transform", "");
      this.ksPreviewZoom(1);
    },

    /**
     * Handle zoom in functionality.
     */
    ksPreviewZoomIn: function (ev) {
      ev.preventDefault();
      var ksScale = this.scale + 0.5;
      this.ksPreviewZoom(ksScale);
    },

    /**
     * Handle zoom out functionality.
     */
    _ksZoomOutPreview: function (ev) {
      ev.preventDefault();
      var ksScale = this.scale - 0.5;
      this.ksPreviewZoom(ksScale);
    },

    ksOnKeyUp: function (ev) {
      switch (ev.which) {
        case $.ui.keyCode.ESCAPE:
          ev.preventDefault();
          this.destroy();
          break;
      }
    },
  });

  return KsListDocumentViewer;
});
