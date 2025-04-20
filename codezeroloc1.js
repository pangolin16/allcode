function zmena() {
    var image = document.getElementById('obraz');
    if (image.src.match("images/separated.svg")) {
      image.src = "images/whole.svg";
    } else {
      image.src = "images/separated.svg";
    }
  }

  function gets1(){var image = document.getElementById('obraz');
    if (image.src.match("whole")) {gets1a();}
   else {gets1b();}}
  function gets2(){var image = document.getElementById('obraz');
    if (image.src.match("whole")) {gets2a();}
   else {gets2b();}}
  function gets3(){var image = document.getElementById('obraz');
    if (image.src.match("whole")) {gets3a();}
   else {gets3b();}}
   function gets4(){var image = document.getElementById('obraz');
    if (image.src.match("whole")) {gets4a();}
   else {gets4b();}}



function gets1a(){let s1=document.getElementById("s1").value
    if(s1<=30&& s1>10){document.getElementById("output1").innerHTML=parseInt(s1)-1}
    else if(s1<=40&& s1>30){document.getElementById("output1").innerHTML=parseInt(s1)}
    else if(s1<=100&& s1>40){document.getElementById("output1").innerHTML=parseInt(s1)+1}
    else if(s1<=200&& s1>100){document.getElementById("output1").innerHTML=parseInt(s1)+1}
    else if(s1<=400&& s1>300){document.getElementById("output1").innerHTML=parseInt(s1)+1}
    else if(s1<=500&& s1>400){document.getElementById("output1").innerHTML=parseInt(s1)+1}
    else if(s1<=600&& s1>500){document.getElementById("output1").innerHTML=parseInt(s1)+5}
    else if(s1<=700&& s1>600){document.getElementById("output1").innerHTML=parseInt(s1)+6}
    else if(s1<=800&& s1>700){document.getElementById("output1").innerHTML=parseInt(s1)+7}
    else if(s1<=1200&& s1>800){document.getElementById("output1").innerHTML=parseInt(s1)+8}
    else if(s1<=1800&& s1>1200){document.getElementById("output1").innerHTML=parseInt(s1)+9}
    else if(s1<=2200&& s1>1800){document.getElementById("output1").innerHTML=parseInt(s1)+10}
    else if(s1<=2500&& s1>2200){document.getElementById("output1").innerHTML=parseInt(s1)+11}
    else if(s1<=3000& s1>2500){document.getElementById("output1").innerHTML=parseInt(s1)+12}
    else if(s1>9999){document.getElementById("output1").innerHTML="#"}
    else if(s1<10){document.getElementById("output1").innerHTML="#"}
else{document.getElementById("output1").innerHTML=Math.round(
parseInt(s1)**0.9995+1)}}


function gets1b(){let s1=document.getElementById("s1").value
    if(s1<=150&& s1>10){document.getElementById("output1").innerHTML=parseInt(s1)+2}
   else if(s1<500){document.getElementById("output1").innerHTML=parseInt(s1)+2}
    else if(s1<=600&& s1>500){document.getElementById("output1").innerHTML=parseInt(s1)+3}
    else if(s1<=700&& s1>600){document.getElementById("output1").innerHTML=parseInt(s1)+4}
    else if(s1<=725&& s1>700){document.getElementById("output1").innerHTML=parseInt(s1)+5}
    else if(s1<=750&& s1>725){document.getElementById("output1").innerHTML=parseInt(s1)+6}
    else if(s1<=3000& s1>750){document.getElementById("output1").innerHTML=parseInt(s1)+7}
    else if(s1>9999){document.getElementById("output1").innerHTML="#"}
    else if(s1<10){document.getElementById("output1").innerHTML="#"}
else{document.getElementById("output1").innerHTML=Math.round(
parseInt(s1)**0.9995+1)}}









    function gets2a(){let s2=document.getElementById("s2").value
        if(s2<600){document.getElementById("output2").innerHTML=parseInt(s2)+2}
        else if(s2<=650&& s2>600){document.getElementById("output2").innerHTML=parseInt(s2)+3}
        else if(s2<=700&& s2>650){document.getElementById("output2").innerHTML=parseInt(s2)+4}
        else if(s2<=1100&& s2>700){document.getElementById("output2").innerHTML=parseInt(s2)+5}
        else if(s2<=1150&& s2>1100){document.getElementById("output2").innerHTML=parseInt(s2)+6}
        else if(s2<=1200&& s2>1150){document.getElementById("output2").innerHTML=parseInt(s2)+7}
        else if(s2<=2200&& s2>1200){document.getElementById("output2").innerHTML=parseInt(s2)+8}
        else if(s2<=2500&& s2>2200){document.getElementById("output2").innerHTML=parseInt(s2)+9}
        else if(s2<=3000& s2>2500){document.getElementById("output2").innerHTML=parseInt(s2)+10}
        else if(s2>9999){document.getElementById("output2").innerHTML="#"}
        else if(s2<10){document.getElementById("output2").innerHTML="#"}
    else{document.getElementById("output2").innerHTML=Math.round(
        parseInt(s2)**0.9995+2)}}


        function gets2b(){let s2=document.getElementById("s2").value
            if(s2<=150&& s2>10){document.getElementById("output2").innerHTML=parseInt(s2)+2}
           else if(s2<450){document.getElementById("output2").innerHTML=parseInt(s2)+2}
            else if(s2<=550&& s2>450){document.getElementById("output2").innerHTML=parseInt(s2)+3}
            else if(s2<=650&& s2>550){document.getElementById("output2").innerHTML=parseInt(s2)+4}
            else if(s2<=750&& s2>650){document.getElementById("output2").innerHTML=parseInt(s2)+5}
            else if(s2<=800&& s2>750){document.getElementById("output2").innerHTML=parseInt(s2)+5}
            else if(s2<=3000& s2>800){document.getElementById("output2").innerHTML=parseInt(s2)+5}
            else if(s2>9999){document.getElementById("output2").innerHTML="#"}
            else if(s2<10){document.getElementById("output2").innerHTML="#"}
        else{document.getElementById("output2").innerHTML=Math.round(
        parseInt(s2)**0.9995+1)}}
        
        
        


        function gets3a(){let s3=document.getElementById("s3").value
            if(s3<600){document.getElementById("output3").innerHTML=parseInt(s3)+2}
            else if(s3<=650&& s3>600){document.getElementById("output3").innerHTML=parseInt(s3)+3}
            else if(s3<=700&& s3>650){document.getElementById("output3").innerHTML=parseInt(s3)+4}
            else if(s3<=1100&& s3>700){document.getElementById("output3").innerHTML=parseInt(s3)+5}
            else if(s3<=1150&& s3>1100){document.getElementById("output3").innerHTML=parseInt(s3)+6}
            else if(s3<=1200&& s3>1150){document.getElementById("output3").innerHTML=parseInt(s3)+7}
            else if(s3<=2200&& s3>1200){document.getElementById("output3").innerHTML=parseInt(s3)+8}
            else if(s3<=2500&& s3>2200){document.getElementById("output3").innerHTML=parseInt(s3)+9}
            else if(s3<=3000& s3>2500){document.getElementById("output3").innerHTML=parseInt(s3)+10}
            else if(s3>9999){document.getElementById("output3").innerHTML="#"}
            else if(s3<10){document.getElementById("output3").innerHTML="#"}
            else{document.getElementById("output3").innerHTML=Math.round( parseInt(s3)**0.9995+2)}}



            function gets3b(){let s3=document.getElementById("s3").value
                if(s3<=150&& s3>10){document.getElementById("output3").innerHTML=parseInt(s3)+2}
               else if(s3<450){document.getElementById("output3").innerHTML=parseInt(s3)+2}
                else if(s3<=550&& s3>450){document.getElementById("output3").innerHTML=parseInt(s3)+3}
                else if(s3<=650&& s3>550){document.getElementById("output3").innerHTML=parseInt(s3)+4}
                else if(s3<=750&& s3>650){document.getElementById("output3").innerHTML=parseInt(s3)+5}
                else if(s3<=800&& s3>750){document.getElementById("output3").innerHTML=parseInt(s3)+5}
                else if(s3<=3000& s3>800){document.getElementById("output3").innerHTML=parseInt(s3)+5}
                else if(s3>9999){document.getElementById("output3").innerHTML="#"}
                else if(s3<10){document.getElementById("output3").innerHTML="#"}
            else{document.getElementById("output3").innerHTML=Math.round(
            parseInt(s3)**0.9995+1)}}
       
            
        
        
        //krabice s ořezy
        function gets4(){let s4=document.getElementById("s4").value
                    if(s4<150){document.getElementById("output4").innerHTML=parseInt(s4)-2}
                    else if(s4<=250 && s4>150){document.getElementById("output4").innerHTML=parseInt(s4)-2}
                    else if(s4<=300&& s4>250){document.getElementById("output4").innerHTML=parseInt(s4)-3}
                    else if(s4<=500 && s4>300){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                    else if(s4<=650 && s4>500){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                    else if(s4<=750 && s4>650){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                else if(s4<=1300 && s4>750){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                else if(s4<=1500 && s4>1300){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                else if(s4<=1650 && s4>1500){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                else if(s4<=1800 && s4>1650){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                else if(s4<=2000&& s4>1800){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                else if(s4<=2500 && s4>2000){document.getElementById("output4").innerHTML=parseInt(s4)-4}
                else if(s4>9999){document.getElementById("output4").innerHTML="#"}
                else if(s4<10){document.getElementById("output4").innerHTML="#"}
                else{document.getElementById("output4").innerHTML=parseInt(s4)-4}}
                
                



  



      $(document).keydown(function(e) {

        // Set self as the current item in focus
        var self = $(':focus'),
            // Set the form by the current item in focus
            form = self.parents('form:eq(0)'),
            focusable;
      
        // Array of Indexable/Tab-able items
        focusable = form.find('input,a,select,button,textarea,div[contenteditable=true]').filter(':visible');
      
        function enterKey(){
          if (e.which === 13 && !self.is('textarea,div[contenteditable=true]')) { // [Enter] key
      
            // If not a regular hyperlink/button/textarea
            if ($.inArray(self, focusable) && (!self.is('a,button'))){
              // Then prevent the default [Enter] key behaviour from submitting the form
              e.preventDefault();
            } // Otherwise follow the link/button as by design, or put new line in textarea
      
            // Focus on the next item (either previous or next depending on shift)
            focusable.eq(focusable.index(self) + (e.shiftKey ? -1 : 1)).focus();
      
            return false;
          }
        }
        // We need to capture the [Shift] key and check the [Enter] key either way.
        if (e.shiftKey) { enterKey() } else { enterKey()  }
      });