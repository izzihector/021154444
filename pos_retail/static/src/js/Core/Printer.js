odoo.define('pos_retail.Printer', function (require) {
    const Printer = require('point_of_sale.Printer');
    const core = require('web.core');
    const _t = core._t;
    const {Gui} = require('point_of_sale.Gui');
    const session = require('web.session');

    Printer.Printer.include({

        htmlToImg: function (receipt) {
            console.log('htmlToImg begin')
            if (!this.pos) {
                this.pos = posmodel
            }
            this.receipt = $('.pos-receipt-print>.pos-receipt');
            if (this.receipt && this.receipt.length == 0) {
                console.log('receipt A4Receipt template')
                const self = this;
                $('.pos-receipt-print').html(receipt);
                const promise = new Promise(function (resolve, reject) {
                    self.receipt = $('.pos-receipt-print>.pos-receipt');
                    if (self.receipt.length == 0) {
                        self.receipt = $('.pos-receipt-print>.pos-receipt-a4');
                    }
                    html2canvas(self.receipt[0], {
                        onparsed: function (queue) {
                            queue.stack.ctx.height = Math.ceil(self.receipt.outerHeight() + self.receipt.offset().top);
                            queue.stack.ctx.width = Math.ceil(self.receipt.outerWidth() + 2 * self.receipt.offset().left);
                        },
                        onrendered: function (canvas) {
                            $('.pos-receipt-print').empty();
                            resolve(self.process_canvas(canvas));
                        },
                        letterRendering: self.pos.htmlToImgLetterRendering(),
                    })
                });
                return promise;
            } else {
                return this._super(receipt);
            }
        },

        _onIoTActionResult: function (data) {
            try {
                this._super(data)
            } catch (e) {
                return Gui.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('Your POS Disconnected Kitchen Printer, please Your POS Setting or Your Internet Connection')
                })
            }
        },
        printHtmlToImage: async function (receipt) {
            let printNumber = 1
            if (this.pos.config.duplicate_receipt && this.pos.config.duplicate_number > 1) {
                printNumber = this.pos.config.duplicate_number
            }
            for (let i = 0; i < printNumber; i++) {
                if (receipt) {
                    this.receipt_queue.push(receipt);
                }
                let image, sendPrintResult;
                while (this.receipt_queue.length > 0) {
                    receipt = this.receipt_queue.shift();
                    image = await this.htmlToImg(receipt);
                    try {
                        sendPrintResult = await this.send_printing_job(image);
                    } catch (error) {
                        // Error in communicating to the IoT box.
                        this.receipt_queue.length = 0;
                        return this.printResultGenerator.IoTActionError();
                    }
                    // rpc call is okay but printing failed because
                    // IoT box can't find a printer.
                    if (!sendPrintResult || sendPrintResult.result === false) {
                        this.receipt_queue.length = 0;
                        return this.printResultGenerator.IoTResultError();
                    }
                }
            }
            return this.printResultGenerator.Successful();

        },

        send_printing_job: function (img) { // TODO: fixed loading times send img to printer, and running background
            if (this.connection && this.connection.server == "http://localhost:8069") {
                return true
            } else {
                return this._super(img);
            }
        },

        open_cashbox: function () {
            if (this.pos.config.proxy_ip) {
                console.warn('open cashbox')
                return this.connection.rpc('/hw_proxy/open_cashbox', {});
            } else {
                return this._super();
            }
        },

        open_cashbox_direct: function () {
            return this.connection.rpc('/hw_proxy/open_cashbox_direct', {})
        },
    });

})
