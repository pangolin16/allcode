function zmena() {
    var image = document.getElementById('obraz');
    if (image.src.match("images/separated.svg")) {
      image.src = "images/whole.svg";
    } else {
      image.src = "images/separated.svg";
    }
  }
function gets1(){var image = document.getElementById('obraz');
    if (image.src.match("separated")) {gets1a();}
   else {gets1b();}}


function gets1a(){
     let s1=document.getElementById("s1").value

     if(s1<=150&& s1>10){document.getElementById("output1").innerHTML=parseInt(s1)+10}
     else if(s1<=250 && s1>150){document.getElementById("output1").innerHTML=parseInt(s1)+11}
     else if(s1<=400&& s1>250){document.getElementById("output1").innerHTML=parseInt(s1)+12}    
     else if(s1<=450 && s1>400){document.getElementById("output1").innerHTML=parseInt(s1)+13}
     else if(s1<=650 && s1>450){document.getElementById("output1").innerHTML=parseInt(s1)+14}
     else if(s1<=950 && s1>650){document.getElementById("output1").innerHTML=parseInt(s1)+15}
 else if(s1<=1300 && s1>950){document.getElementById("output1").innerHTML=parseInt(s1)+16}
 else if(s1<=1750 && s1>1300){document.getElementById("output1").innerHTML=parseInt(s1)+17}
 else if(s1<=1800 && s1>1750){document.getElementById("output1").innerHTML=parseInt(s1)+18}
 else if(s1<=1900 && s1>1800){document.getElementById("output1").innerHTML=parseInt(s1)+19}
 else if(s1<=2000&& s1>1900){document.getElementById("output1").innerHTML=parseInt(s1)+20}
 else if(s1<=2500 && s1>2000){document.getElementById("output1").innerHTML=parseInt(s1)+21}
 else if(s1>9999){document.getElementById("output1").innerHTML="#"}
 else if(s1<10){document.getElementById("output1").innerHTML="#"}
 else{document.getElementById("output1").innerHTML=Math.round(parseInt(s1)+(Math.log(parseInt(s1))*5.756+22.2139))
  }}

  function gets1b(){let s1=document.getElementById("s1").value
    if(s1<150){document.getElementById("output1").innerHTML=parseInt(s1)-6
    }else if(s1<=250 && s1>150){document.getElementById("output1").innerHTML=parseInt(s1)-6}
    else if(s1<=300&& s1>250){document.getElementById("output1").innerHTML=parseInt(s1)-6}
    else if(s1<=500 && s1>300){document.getElementById("output1").innerHTML=parseInt(s1)-6} //krabice -19 --->-6
    else if(s1<=650 && s1>500){document.getElementById("output1").innerHTML=parseInt(s1)-6}
    else if(s1<=750 && s1>650){document.getElementById("output1").innerHTML=parseInt(s1)-6}
 else if(s1<=1300 && s1>750){document.getElementById("output1").innerHTML=parseInt(s1)-6}
 else if(s1<=1500 && s1>1300){document.getElementById("output1").innerHTML=parseInt(s1)-6}
 else if(s1<=1650 && s1>1500){document.getElementById("output1").innerHTML=parseInt(s1)-6}
 else if(s1<=800 && s1>1650){document.getElementById("output1").innerHTML=parseInt(s1)-6}
 else if(s1<=2000&& s1>1800){document.getElementById("output1").innerHTML=parseInt(s1)-6}
 else if(s1<=2500 && s1>2000){document.getElementById("output1").innerHTML=parseInt(s1)-6}
 else if(s1>9999){document.getElementById("output1").innerHTML="#"}
 else if(s1<10){document.getElementById("output1").innerHTML="#"}
 else{document.getElementById("output1").innerHTML=parseInt(s1)-19}}
 





 function gets2(){var image = document.getElementById('obraz');
    if (image.src.match("separated")) {gets2a();}
   else {gets2b();}}



    function gets2a(){let s2=document.getElementById("s2").value
        if(s2<150){document.getElementById("output2").innerHTML=parseInt(s2)
        }else if(s2<=250 && s2>150){document.getElementById("output2").innerHTML=parseInt(s2)+1}
        else if(s2<=300&& s2>250){document.getElementById("output2").innerHTML=parseInt(s2)+2}
        else if(s2<=500 && s2>300){document.getElementById("output2").innerHTML=parseInt(s2)+3}
        else if(s2<=650 && s2>500){document.getElementById("output2").innerHTML=parseInt(s2)+4}
        else if(s2<=950 && s2>650){document.getElementById("output2").innerHTML=parseInt(s2)+5}
    else if(s2<=1300 && s2>950){document.getElementById("output2").innerHTML=parseInt(s2)+6}
    else if(s2<=1500 && s2>1300){document.getElementById("output2").innerHTML=parseInt(s2)+7}
    else if(s2<=1650 && s2>1500){document.getElementById("output2").innerHTML=parseInt(s2)+8}
    else if(s2<=1800 && s2>1650){document.getElementById("output2").innerHTML=parseInt(s2)+9}
    else if(s2<=2000&& s2>1800){document.getElementById("output2").innerHTML=parseInt(s2)+10}
    else if(s2<=2500 && s2>2000){document.getElementById("output2").innerHTML=parseInt(s2)+11}
    else if(s2>9999){document.getElementById("output2").innerHTML="#"}
    else if(s2<10){document.getElementById("output2").innerHTML="#"}
    else{document.getElementById("output2").innerHTML=Math.round(parseInt(s2)+(Math.log(parseInt(s2))*4.9755+32.7087))}}

    function gets2b(){let s2=document.getElementById("s2").value
        if(s2<150){document.getElementById("output2").innerHTML=parseInt(s2)
        }else if(s2<=250 && s2>150){document.getElementById("output2").innerHTML=parseInt(s2)}
        else if(s2<=300&& s2>250){document.getElementById("output2").innerHTML=parseInt(s2)}
        else if(s2<=500 && s2>300){document.getElementById("output2").innerHTML=parseInt(s2)+1}
        else if(s2<=650 && s2>500){document.getElementById("output2").innerHTML=parseInt(s2)+2}
        else if(s2<=950 && s2>650){document.getElementById("output2").innerHTML=parseInt(s2)+2}
    else if(s2<=1300 && s2>950){document.getElementById("output2").innerHTML=parseInt(s2)+2}
    else if(s2<=1500 && s2>1300){document.getElementById("output2").innerHTML=parseInt(s2)+2}
    else if(s2<=1650 && s2>1500){document.getElementById("output2").innerHTML=parseInt(s2)+2}
    else if(s2<=1800 && s2>1650){document.getElementById("output2").innerHTML=parseInt(s2)+2}
    else if(s2<=2000&& s2>1800){document.getElementById("output2").innerHTML=parseInt(s2)+2}
    else if(s2<=2500 && s2>2000){document.getElementById("output2").innerHTML=parseInt(s2)+2}
    else if(s2>9999){document.getElementById("output2").innerHTML="#"}
    else if(s2<10){document.getElementById("output2").innerHTML="#"}
    else{document.getElementById("output2").innerHTML=Math.round(parseInt(s2)+(Math.log(parseInt(s2))*4.9755+32.7087))}}
    


    function gets3(){var image = document.getElementById('obraz');
        if (image.src.match("separated")) {gets3a();}
       else {gets3b();}}
    
    



    function gets3a(){let s3=document.getElementById("s3").value
            if(s3<150){document.getElementById("output3").innerHTML=parseInt(s3)
            }else if(s3<=250 && s3>150){document.getElementById("output3").innerHTML=parseInt(s3)+1}
        else if(s3<=300&& s3>250){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=500 && s3>300){document.getElementById("output3").innerHTML=parseInt(s3)+3}
        else if(s3<=650 && s3>500){document.getElementById("output3").innerHTML=parseInt(s3)+4}
        else if(s3<=950 && s3>650){document.getElementById("output3").innerHTML=parseInt(s3)+5}
    else if(s3<=1300 && s3>950){document.getElementById("output3").innerHTML=parseInt(s3)+6}
    else if(s3<=1500 && s3>1300){document.getElementById("output3").innerHTML=parseInt(s3)+7}
    else if(s3<=1650 && s3>1500){document.getElementById("output3").innerHTML=parseInt(s3)+8}
    else if(s3<=1800 && s3>1650){document.getElementById("output3").innerHTML=parseInt(s3)+9}
    else if(s3<=2000&& s3>1800){document.getElementById("output3").innerHTML=parseInt(s3)+10}
    else if(s3<=2500 && s3>2000){document.getElementById("output3").innerHTML=parseInt(s3)+11}
    else if(s3>9999){document.getElementById("output3").innerHTML="#"}
    else if(s3<10){document.getElementById("output3").innerHTML="#"}
        else{document.getElementById("output3").innerHTML=Math.round(parseInt(s3)+(Math.log(parseInt(s3))*4.9755+32.7087))}}

        function gets3b(){let s3=document.getElementById("s3").value
            if(s3<150){document.getElementById("output3").innerHTML=parseInt(s3)
            }
        else if(s3<=250 && s3>150){document.getElementById("output3").innerHTML=parseInt(s3)}
        else if(s3<=300&& s3>250){document.getElementById("output3").innerHTML=parseInt(s3)+1}
        else if(s3<=500 && s3>300){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=650 && s3>500){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=950 && s3>650){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=1300 && s3>950){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=1500 && s3>1300){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=1650 && s3>1500){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=1800 && s3>1650){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=2000&& s3>1800){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3<=2500 && s3>2000){document.getElementById("output3").innerHTML=parseInt(s3)+2}
        else if(s3>9999){document.getElementById("output3").innerHTML="#"}
        else if(s3<10){document.getElementById("output3").innerHTML="#"}
        else{document.getElementById("output3").innerHTML=Math.round(parseInt(s3)+(Math.log(parseInt(s3))*4.9755+32.7087))}}

        function gets4(){var image = document.getElementById('obraz');
            if (image.src.match("separated")) {gets4a();}
           else {gets4b();}}
        
        


            function gets4a(){let s4=document.getElementById("s4").value
                if(s4<150){document.getElementById("output4").innerHTML=parseInt(s4)}
            else if(s4<=250 && s4>150){document.getElementById("output4").innerHTML=parseInt(s4)+1}
            else if(s4<=300&& s4>250){document.getElementById("output4").innerHTML=parseInt(s4)+2}
            else if(s4<=500 && s4>300){document.getElementById("output4").innerHTML=parseInt(s4)+3}
            else if(s4<=650 && s4>500){document.getElementById("output4").innerHTML=parseInt(s4)+4}
            else if(s4<=950 && s4>650){document.getElementById("output4").innerHTML=parseInt(s4)+5}
        else if(s4<=1300 && s4>950){document.getElementById("output4").innerHTML=parseInt(s4)+6}
        else if(s4<=1500 && s4>1300){document.getElementById("output4").innerHTML=parseInt(s4)+7}
        else if(s4<=1650 && s4>1500){document.getElementById("output4").innerHTML=parseInt(s4)+8}
        else if(s4<=1800 && s4>1650){document.getElementById("output4").innerHTML=parseInt(s4)+9}
        else if(s4<=2000&& s4>1800){document.getElementById("output4").innerHTML=parseInt(s4)+10}
        else if(s4<=2500 && s4>2000){document.getElementById("output4").innerHTML=parseInt(s4)+11}
        else if(s4>9999){document.getElementById("output4").innerHTML="#"}
        else if(s4<10){document.getElementById("output4").innerHTML="#"}
            else{document.getElementById("output4").innerHTML=Math.round(parseInt(s4)+(Math.log(parseInt(s4))*4.9755+32.7087))}}





    function gets4b(){let s4=document.getElementById("s4").value
        if(s4<150){document.getElementById("output4").innerHTML=parseInt(s4)}
    else if(s4<=250 && s4>150){document.getElementById("output4").innerHTML=parseInt(s4)+1}
    else if(s4<=300&& s4>250){document.getElementById("output4").innerHTML=parseInt(s4)+2}
    else if(s4<=500 && s4>300){document.getElementById("output4").innerHTML=parseInt(s4)+2}
    else if(s4<=650 && s4>500){document.getElementById("output4").innerHTML=parseInt(s4)+2}
    else if(s4<=950 && s4>650){document.getElementById("output4").innerHTML=parseInt(s4)+2}
else if(s4<=1300 && s4>950){document.getElementById("output4").innerHTML=parseInt(s4)+2}
else if(s4<=1500 && s4>1300){document.getElementById("output4").innerHTML=parseInt(s4)+2}
else if(s4<=1650 && s4>1500){document.getElementById("output4").innerHTML=parseInt(s4)+2}
else if(s4<=1800 && s4>1650){document.getElementById("output4").innerHTML=parseInt(s4)+2}
else if(s4<=2000&& s4>1800){document.getElementById("output4").innerHTML=parseInt(s4)+2}
else if(s4<=2500 && s4>2000){document.getElementById("output4").innerHTML=parseInt(s4)+2}
else if(s4>9999){document.getElementById("output4").innerHTML="#"}
else if(s4<10){document.getElementById("output4").innerHTML="#"}
    else{document.getElementById("output4").innerHTML=Math.round(parseInt(s4)+(Math.log(parseInt(s4))*4.9755+32.7087))}}


    const clearButton = document.getElementById('clearButton');

    // Add an event listener to the button
    clearButton.addEventListener('click', function() {
      // Clear the value of the input fields
      s1.value = '';
      s2.value = '';
      s3.value = '';
       s4.value = '';
      
      console.log('Input fields cleared');
    });