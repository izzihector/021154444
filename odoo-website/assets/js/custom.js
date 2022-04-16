//
jQuery(document).on('click', '.mega-dropdown', function (e) {
  e.stopPropagation();
});

document.addEventListener('DOMContentLoaded', function () {
  // When the user scrolls the page, execute myFunction
  window.onscroll = function () {
    myFunction();
  };
  // Get the header
  var header = document.querySelector('header');
  var navBar = document.querySelector('header .navbar');

  // Get the offset position of the navbar
  var sticky = header.offsetTop;
  // Add the sticky class to the header when you reach its scroll position. Remove "sticky" when you leave the scroll position
  function myFunction() {
    if (window.pageYOffset > sticky) {
      header.classList.add('sticky');
      navBar.classList.add('nav-padding');
    } else {
      header.classList.remove('sticky');
      navBar.classList.remove('nav-padding');
    }
  }

  // Hover Button arrow
  let allButton = document.getElementsByClassName('btn');
  // console.log(allButton);
  let index = 0;

  for (var i = 0; i < allButton.length; i++) {
    if (allButton[i].classList.contains('lift')) {
    } else {
      let span = document.createElement('span');
      span.classList.add('b-icon');
      span.innerHTML =
        '<i class="fa fa-arrow-right" aria-hidden="true" style=""></i>';
      allButton[i].appendChild(span);
    }
  }
});
// DOMContentLoaded  end
