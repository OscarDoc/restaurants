

window.onload = () => {

	(function restaurants_html(){
		// Show a restaurant's action buttons only when hovering it
		function toggleActions(){
			$(this).find('a:not(.btn-default)').toggleClass('hidden');
		};
		$('#restaurant-list .btn-group').hover(toggleActions, toggleActions);
	})();


	(function showmenu_html(){
		// Adjust all menu item boxes to have the same height
		var maxHeight = 0;
		const thumbs = $('.thumbnail');
		thumbs.each(function(){
			var h = $(this).height();
			if(h > maxHeight) maxHeight = h;
		});
		thumbs.height(maxHeight);
	})();
	

	// Bind a function to any input-file field to check the upload size before trying to send it
	// Flask would return us an HTTP:413 error in any case, but this way we can give feedback to the user
	$('input[type="file"]').bind('change', function() {
		var fileSize = this.files[0].size;
		// If weights less than 1Mb, it's OK
		if(fileSize < 1024*1024) return; 
		// Else show a message and reset the input
		alert('File size too big! Max image size is 1 Megabyte.');
		this.value = "";
	});
};