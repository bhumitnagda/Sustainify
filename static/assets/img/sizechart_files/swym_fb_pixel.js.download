(function(){
 var startListening = function(){
   window._swat.evtLayer.addEventListener(SwymTracker.JSEvents.addedToWishlist, function(e){
     var evtData = e.detail.d;

 /* Sample data format that gets passed
   evtData format -
     {
        et: 4 for wishlist,
        dt: // product title
        du: // product full url
        epi: // variant id
        empi: // product id
        pr: // price
        iu: // image url
     };
 */

 /* Calling the FB Pixel tracking function w/ the right args */

     window.fbq("track", "AddToWishlist", {
         content_ids: [evtData.empi],
         content_type: "product_group",
         content_name: evtData.dt,
         content_category: evtData.ct,
         currency: SwymUtils.getOGData()["og:price:currency"] || (window.ShopifyAnalytics && window.ShopifyAnalytics.meta ? window.ShopifyAnalytics.meta.currency : ''),
         value: evtData.pr
       });
   });
 };
 if(!window._swat){
   if(!window.SwymCallbacks){
     window.SwymCallbacks = [];
   }
   window.SwymCallbacks.push(startListening);
 }else{
   startListening();
 }
})();
