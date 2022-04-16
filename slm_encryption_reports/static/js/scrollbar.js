(function () {
  let container = $('.o_account_reports_no_print')
  let main_container = $('.o_account_reports_body')
  let table_wrapper = $('.table-responsive')
  
  function scrollBars (update = false) {
    $('.o_account_reports_no_print').ready(() => {
      let position = $('.o_content').position()
      let top = position.top
      let height = window.innerHeight
      let body_height = height - top
      if (!update) {
        body_height = body_height - 18
      }
      let table_width = table_wrapper.width()
      container.css('cssText', 'max-width: ' + table_width + 'px !important')
      container.width(table_width + 'px')
      main_container.height(body_height + 'px')
      if (update) {
        main_container.width('100%')
        main_container.css('overflow', 'auto')
      }
    }, update)
  }
  
  setTimeout(() => {
    scrollBars()
  }, 500)
  $(window).on('resize', function () {
    scrollBars(true)
  })
  
  function stickyHeader () {
    let header_sticked = {}, width, height_header, height, class_name, headers_height, total_width, max_width,
      class_name_selector_length, class_name_selector,class_unsticked
    let sticky_selector = 'tr[class*=sticky_header]'
    let wrapper_top = $('.o_content').position().top
    let table_wrapper_left = table_wrapper.position().left
    $(sticky_selector).each(function () {
        class_name = $(this).attr('class').match(/\b\w+sticky_header/i)[0]
        height = $(this).outerHeight()
        if (!header_sticked.hasOwnProperty(class_name)) {
          header_sticked[class_name] = {'height': height}
        } else {
          header_sticked[class_name]['height'] += height
        }
      if (!$(this).hasClass('sticked')) {
        //set td width
        total_width = 0
        $(this).find('td').each(function () {
          if (!$(this).hasClass('width')) {
            width = $(this).outerWidth()
            $(this).addClass('width')
            $(this).css('min-width', width + 'px')
            total_width += width
          }
        })
        // set tr width
        if (!$(this).hasClass('width_tr')) {
          $(this).css('min-width', total_width) + 'px'
          $(this).attr('data-width', total_width)
          $(this).addClass('width_tr')
        }
      }
    })
    console.log(header_sticked)
    $(sticky_selector).each(function () {
      class_name = $(this).attr('class').match(/\b\w+sticky_header/i)[0]
      class_name_selector = $('.' + class_name)
      console.log(class_unsticked, class_name, $(this).attr('class'))
      if (!$(this).hasClass('sticked')) {
        let top = $(this).position().top
        height_header = header_sticked[class_name]['height']
        if (top <= 0 && ((height_header + top) > 0)) {
          headers_height = 0
          max_width = 0
          class_name_selector.each(function () {
            width = $(this).attr('data-width')
            if (width > max_width) {
              max_width = width
            }
          })
          class_name_selector_length = class_name_selector.length
          class_name_selector.each(function (index) {
            $(this).addClass('sticked').css({'top': headers_height + wrapper_top})
            height = $(this).outerHeight()
            headers_height += height
            $(this).css('min-width', max_width + 'px')
            if ((index + 1) === class_name_selector_length) {
              $(this).addClass('last_tr')
            }
          })
        } else {
          headers_height = 0
          $('.sticked').each(function () {
            height = $(this).outerHeight()
            headers_height += height
          })
          if (headers_height > 0) {
            if (top <= headers_height) {
              $('.sticked').each(function () {
                $(this).removeClass('sticked')
              })
              class_unsticked = class_name
            }
          }
        }
      } else {
        $('.' + class_name).each(function () {
          $(this).addClass('sticked').css({'left': table_wrapper_left})
        })
      }
    })
  }
  
  main_container.scroll(function () {
    // stickyHeader()
  })
})()