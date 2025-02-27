$('document').ready(function () {

    if (document.getElementById('nav_news_slab_holder') != null)
        adjustBottomSlab();
    /*Not required anymore. Accessbar is not positioned absolutely inside a relatively positioned mast_instance
         *if(document.getElementById('access_bar')!=null)
        adjustAccessBar();
        */
    positionTeamListNav();

    $(window).resize(function () {
        if (document.getElementById('nav_news_slab_holder') != null)
            adjustBottomSlab();
        /*Not required anymore. Accessbar is not positioned absolutely inside a relatively positioned mast_instance
         *if(document.getElementById('access_bar')!=null)
            adjustAccessBar();
        */
        positionTeamListNav();
    });
    if (document.getElementById('login_form') != null) {
        $("#login_form").validate();
        $("#login_form").submit(function () {
            if ($("#password").val() !== "") {
                var new_password = hasher($('#password').val(), $('#salt').val());
                $("#password").val(new_password);
                $("#salt").val("");
            }
        });
    }


    /*
     *  Showing and hiding password in change password 
     */

    if ($('#change_password_show_password').is(':checked')) {
        $('#new_password_container').html('<input type="text" name="new_password" id="new_password_text" class="newPassword required" />');
    } else {
        $('#new_password_container').html('<input type="password" name="new_password" id="new_password_password" class="newPassword required" />');
    }
    $("#change_password_show_password").live('click', function () {
        var password;
        if ($('.newPassword').attr('type') === "password") {
            password = $('#new_password_password').val();
            $('#new_password_container').html('<input type="text" name="new_password" id="new_password_text" class="newPassword required" />');
            $('#new_password_text').val(password);
        } else {
            password = $('#new_password_text').val();
            $('#new_password_container').html('<input type="password" name="new_password" id="new_password_password" class="newPassword required" />');
            $('#new_password_password').val(password);
        }
    });

    if (window.roleSpecificScripts) {
        roleSpecificScripts();
    }

    /*
 binding the click event for showing and hiding the hidden boxes continer
    
     */
    //closing the global notifications bar
    $('span.global_notification_close').click(function () {
        $('div.global_notification').slideUp(70);
    });
    //closing hidden boxes container
    $('.close_hidden_container').click(function () {
        $('#hidden_boxes').hide();
        $('#hidden_boxes > div').hide();
    });
    //mailbox button action
    $('#mailbox_button').click(function () {
        $('#hidden_boxes').show();
        $('.hidden_box').hide();
        $('#mailbox_container').show();
        /*$('#hidden_boxes').css({
                top:$(window).scrollTop()
            });
            */
    });
    $('#mailbox_sent_button').click(function () {
        $('#hidden_boxes').show();
        $('.hidden_box').hide();
        $('#mailbox_sent_container').show();
        /*$('#hidden_boxes').css({
                top:$(window).scrollTop()
            });
            */
    });
    //add news button action
    $('#add_news').click(function () {
        $('#hidden_boxes').show();
        $('.hidden_box').hide();
        $('#news_full_container').show();
        $('#compose_news_container').show();
        $('#news_title').html('Add news');
        /*$('#hidden_boxes').css({
                top:$(window).scrollTop()
            });
            */
    });
    $('#news_tickr').click(function () {
        $('#hidden_boxes').show();
        $('.hidden_box').hide();
        $('#news_full_container').show();
        $('#news_inbox_container').show();
        $('#news_title').html('News items');
        /*$('#hidden_boxes').css({
                top:$(window).scrollTop()
            });
            */
    });

    //stockts and trends action
    $('#stock_feed').click(function () {
        window.location = "stocks_and_trends.jsp";
    });
    /*
     handling events for mailbox messaging
     */
    //switching between inbox and compose pane
    $('#mail_inbox').click(function () {
        $('#mailbox_nav li').removeClass('active');
        $(this).addClass('active');
        $('.mailbox_content').hide();
        $('#mail_inbox_container').show();
    });
    $('#mail_sent_to').click(function () {
        $('#mailbox_nav li').removeClass('active');
        $(this).addClass('active');
        $('.mailbox_content').hide();
        $('#mail_sent_container').show();
    });
    $('#compose_mail').click(function () {
        $('#mailbox_nav li').removeClass('active');
        $(this).addClass('active');
        $('.mailbox_content').hide();
        $('#compose_mail_container').show();
    });

    /*
     Cosing notifications
     */
    $('.notif_message').click(function () {
        $(this).hide();
    });

    /*
     Displaying and hiding team List
     */
    $('li#teams').click(function () {

        $('#team_list_nav').toggle();
        new_positionTeamListNav();
    });

    /*
     Displaying and hiding plants pages
     */
    $('li#plants').click(function () {
        $('#plants_list_nav').toggle();
        //positionTeamListNav();
        positionPlantsListNav();
    });

    /*add classes to table header and selects*/
    $('table').addClass('data_table');
    $('select').addClass('select_style');
});

function adjustBottomSlab() {
    var winWidth = $(window).width();
    if (winWidth <= 1001) {
        $('#nav_news_slab_holder').removeClass('stick_bottom').addClass('stay_top');
        $('body').addClass('margined');
    } else {
        $('#nav_news_slab_holder').removeClass('stay_top').addClass('stick_bottom');
        $('body').removeClass('margined');
    }
}

/*Not required anymore. Accessbar is not positioned absolutely inside a relatively positioned mast_instance
         *
function adjustAccessBar(){
    var winWidth=$(window).width();
    if(winWidth<=1001){
        $('#access_bar').removeClass('position_right').addClass('position_left');
    }
    else{
        $('#access_bar').removeClass('position_left').addClass('position_right');
    }
}
*/

function positionTeamListNav() {
//    alert('hello');
    var winWidth = $(window).width();
    if (document.getElementById('team_list_nav') != null) {
        var posLeft = $('li#teams').offset().left;
        if (winWidth <= 1001) {
            $('#team_list_nav').css({
                left: posLeft,
                top: $('li#teams').offset().top + 30,
                bottom: 'auto'
            });
        } else {
            $('#team_list_nav').css({
                left: posLeft,
                bottom: $(window).height() - $('li#teams').offset().top,
                top: 'auto'
            });
        }
    }
}

function new_positionTeamListNav() {
    var winWidth = $(window).width();
    if (document.getElementById('team_list_nav') != null) {
        var posLeft = $('li#teams').offset().left + 30;
        if (winWidth <= 1001) {
            $('#team_list_nav').css({
                left: posLeft,
                top: $('li#teams').offset().top + 30,
                bottom: 0
            });
        } else {
            $('#team_list_nav').css({
                left: posLeft + 10,
                top: $(window).height() - $('li#teams').offset().bottom,
                bottom: 0
            });
        }
    }

}

function positionPlantsListNav() {
    var winWidth = $(window).width();
    if (document.getElementById('plants_list_nav') != null) {
        var posLeft = $('li#plants').offset().left;
        if (winWidth <= 1001) {
            $('#plants_list_nav').css({
                left: posLeft,
                top: $('li#plants').offset().top + 30,
                bottom: 'auto'
            });
        } else {
            $('#plants_list_nav').css({
                left: posLeft,
                bottom: $(window).height() - $('li#plants').offset().top,
                top: 'auto'
            });
        }
    }
}


/* 
 * Ajax Calls
 * */

//ajax call for co2 bid book
function getCo2BidBook() {
    var roundId = $('#roundIdCo2BidBook').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_co2market_bidbook.jsp', data, 'ajax_co2_market_bidbook', null, null);
}

//ajax call for carbontax
function getCarbonTax() {
    var roundId = $('#round_carbon_tax').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_carbon_tax.jsp', data, 'ajax_carbon_tax', null, null);
}


//ajax call for power_exchangeresults_bidbook
function getPowerExchangeResultsBidBook() {
    var roundId = $('#roundIdPowerExchangeResultsBidBook').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_power_exchangeresults_bidbook.jsp', data, 'ajax_powerexchangeresults_bidbook', null, null);
}

//ajax call for power_exchangeresults_bidbook
function getPeakPowerExchangeResultsBidBook() {
    var roundId = $('#allRoundIdPowerExchangeResultsBidBook').val();
    var data = "roundId=" + roundId;
    //ajaxRequest('GET','pages/ajax_peak_power_exchangeresults_bidbook.jsp',data,'ajax_peak_powerexchangeresults_bidbook',null,null);
    ajaxRequest('GET', '../commonPages/ajax_peak_power_exchangeresults_bidbook.jsp', data, 'ajax_peak_powerexchangeresults_bidbook', null, null);
}

//ajax call for power_exchangeresults_bidbook
function getOffPeakPowerExchangeResultsBidBook() {
    var roundId = $('#allRoundIdPowerExchangeResultsBidBookOffPeak').val();
    //alert(roundId);
    var data = "roundId=" + roundId;
    //ajaxRequest('GET','pages/ajax_offpeak_power_exchangeresults_bidbook.jsp',data,'ajax_offpeak_powerexchangeresults_bidbook',null,null);
    ajaxRequest('GET', '../commonPages/ajax_offpeak_power_exchangeresults_bidbook.jsp', data, 'ajax_offpeak_powerexchangeresults_bidbook', null, null);
}

//ajax call for power_exchangeresults_bidbook
function getShoulderPowerExchangeResultsBidBook() {
    var roundId = $('#allRoundIdPowerExchangeResultsBidBookShoulder').val();
    var data = "roundId=" + roundId;
    //ajaxRequest('GET','pages/ajax_shoulder_power_exchangeresults_bidbook.jsp',data,'ajax_shoulder_powerexchangeresults_bidbook',null,null);
    ajaxRequest('GET', '../commonPages/ajax_shoulder_power_exchangeresults_bidbook.jsp', data, 'ajax_shoulder_powerexchangeresults_bidbook', null, null);
}

//ajax call for teampeak_power_exchangeresults_bidbook
function getTeamPeakPowerExchangeResultsBidBook() {
    var roundId = $('#roundIdPowerExchangeResultsBidBookPeak').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_peak_powerexchangeresults_bidbook.jsp', data, 'ajax_team_peak_powerexchangeresults_bidbook', null, null);

}

//ajax call for teamoffpeak_power_exchangeresults_bidbook
function getTeamoffpeakPowerExchangeResultsBidBook() {
    var roundId = $('#roundIdPowerExchangeResultsBidBookOffPeak').val();
    //alert(roundId);
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_offpeak_powerexchangeresults_bidbook.jsp', data, 'ajax_team_offpeak_powerexchangeresults_bidbook', null, null);

}


//ajax call for teamoffpeak_power_exchangeresults_bidbook
function getTeamshoulderPowerExchangeResultsBidBook() {
    var roundId = $('#roundIdPowerExchangeResultsBidBookShoulder').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_shoulder_powerexchangeresults_bidbook.jsp', data, 'ajax_team_shoulder_powerexchangeresults_bidbook', null, null);

}

//ajax call for power_exchangeresults_graph
function getPowerExchangeResultsGraph(type) {
    var roundId = $('#roundIdPowerExchangeResults_peakgraph').val();
    var data = "roundId=" + roundId + "&type=" + type;
    ajaxRequest('GET', 'pages/ajax_power_exchangeresults_graph.jsp', data, 'ajax_powerexchangeresults_graph', null, null);

}

//ajax call for power_exchangeresults_graph
function getPeakPowerExchangeResultsGraph() {
    var roundId = $('#roundIdPowerExchangeResults_peakgraph').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_peakpower_exchangeresults_graph.jsp', data, 'ajax_powerexchangeresults_peakgraph', null, null);
}

//ajax call for power_exchangeresults_graph
function getOffPeakPowerExchangeResultsGraph() {
    var roundId1 = $('#roundIdPowerExchangeResults_offpeakgraph').val();
    var data = "roundId1=" + roundId1;
    ajaxRequest('GET', 'pages/ajax_offpeakpower_exchangeresults_graph.jsp', data, 'ajax_powerexchangeresults_offpeakgraph', null, null);
}

//ajax call for power_exchangeresults_graph
function getShoulderPowerExchangeResultsGraph() {
    var roundId2 = $('#roundIdPowerExchangeResults_shoulderpeakgraph').val();
    var data = "roundId2=" + roundId2;
    ajaxRequest('GET', 'pages/ajax_shoulderpower_exchangeresults_graph.jsp', data, 'ajax_powerexchangeresults_shouldergraph', null, null);
}

//ajax call for previous round bids
function getPreviousRoundBidsGraph() {
//    /alert("hi");
    var roundId3 = $('#previous_round_bids_graph').val();
    var data = "roundId3=" + roundId3;
    ajaxRequest('GET', 'pages/ajaxPreviousRoundBids.jsp', data, 'ajax_previous_round_bids_graph', null, null);

}

//ajax call for gElectricityGenerated
function getElectricityGenerated() {
    var roundId = $('#roundIdElectricityGenerated').val();
    var data = "roundId=" + roundId;

    ajaxRequest('GET', 'pages/ajax_electricity_production.jsp', data, 'ajax_electricity_generated', null, null);
}


//ajax call for carbonmarket results
function getCarbonMarketResults() {
    var roundId = $('#roundId_co2market-results').val();
    var data = "roundId=" + roundId;
    //alert(data);
    //ajaxRequest('GET','pages/ajax_co2_results.jsp',data,'ajax_co2_results',null,null);
    ajaxRequest('GET', '../commonPages/ajax_co2_results.jsp', data, 'ajax_co2_results', null, null);

}

//ajax call for carbonmarket results
function getTeamPastCarbonBids() {
    var roundId = $('#team_co2past_bids').val();
    var data = "roundId=" + roundId;
    //alert(data);
    //ajaxRequest('GET','pages/ajax_co2_results.jsp',data,'ajax_co2_results',null,null);
    ajaxRequest('GET', 'pages/ajax_team_past_co2_bids.jsp', data, 'ajax_team_past_co2_bids', null, null);

}

//ajax call for gettinf selected period type for livemarkets

function getPeriodForLiveMarkets() {
    var period = $('#period_livemarket').val();
    var data = "period=" + period;
    ajaxRequest('GET', 'pages/ajax_electricity_livemarkets.jsp', data, 'ajax_electricity_livemarkets', null, null);
}

//ajax call for gettinf selected period type for livemarkets

function getDemandForLiveMarkets() {
    var period = $('#demand_livemarket').val();
    var data = "period=" + period;
    ajaxRequest('GET', 'pages/ajax_electricity_livemarkets_demandfunction.jsp', data, 'ajax_electricity_livemarkets_demandfunction', null, null);
}

//ajax call for biddingbehaviorgraph

function getBiddingBehaviorGraph() {
    var roundId = $('#roundIdbidding_behavior_graph').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_bidding_behavior.jsp', data, 'ajax_bidding_behavior', null, null);
}

//ajax call for NetAvailablePower graph

function getNetAvailablePowerGraph() {
    var roundId = $('#team_roundId_netpower_available_graph').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_available_capacity_graph.jsp', data, 'ajax_available_capacity', null, null);
}

//ajax call for NetAvailablePower graph

function getGenerationPortfolioGraph() {
    var roundId = $('#team_generation_portfolio').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_generation_portfolio_graph.jsp', data, 'ajax_generation_portfolio', null, null);
}

//ajax call for getting team bidding and available 
function getTeamBiddingAvailableCapacity() {
    var roundId = $('#roundId_team_live_bidding').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_bidding_available.jsp', data, 'ajax_team_livebidding_available', null, null);
}


//ajax call for teambiddingbehaviorgraph

function team_getBiddingBehaviorGraph() {
    var roundId = $('#team_roundIdbidding_behavior_graph').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_biddingbehavior.jsp', data, 'ajax_team_bidding_behavior', null, null);
}


//ajax call for plantportfolio
function getTeamPlantPortFolio() {
    var roundId = $('#team_roundId_plantportfolio').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_plantportfolio.jsp', data, 'team_plantportfolio', null, null);
}

//ajax call for power_exchangeresults_graph
function getDemandFunction() {
    var roundId = $('#electricity_demand').val();
    var data = "roundId=" + roundId;

    ajaxRequest('GET', '../commonPages/ajax_electricitydemandfunction.jsp', data, 'ajax_electricity_demandfunction', null, null);

}

//ajax function for parsing excel file
function parse_excel_ebids() {
    var data = "";
    ajaxRequest('GET', 'pages/ajax_submit_elecbids.jsp', data, 'ajax_electricity_bids', null, null);
}

//ajax function for parsing excel file
function parse_excel_co2bids() {
    var data = "";
    ajaxRequest('GET', 'pages/ajax_submit_carbonbids.jsp', data, 'ajax_carbon_bids', null, null);
}

//ajax function for parsing excel file
function parse_excel_carbonsuppliedbids() {
    var data = "";
    //alert("hi");
    ajaxRequest('GET', 'pages/ajax_submit_carbonsuppliedbids.jsp', data, 'ajax_carbon_suppliedbids', null, null);
}


// method to save graph as a PNG image
function saveFlotGraphAsPNG(placeholderID) {

    var divobj = document.getElementById(placeholderID);

    var oImg = Canvas2Image.saveAsPNG(divobj.childNodes[0], true);

    if (!oImg) {
        alert("Sorry, this browser is not capable of saving PNG files!");
        return false;
    }

    oImg.id = "canvasimage";

    document.getElementById(placeholderID).removeChild(document.getElementById(placeholderID).childNodes[0]);
    // document.getElementById(targetID).removeChild(document.getElementById(targetID).childNodes[0]);
    document.getElementById(placeholderID).appendChild(oImg);

}


//ajax call for net power available
function getTeamNetAvailablePower() {
    var roundId = $('#team_roundId_netpower_available').val();
    var data = "roundId=" + roundId;
    ajaxRequest('GET', 'pages/ajax_team_netavailable_powergeneration.jsp', data, 'team_netpower_available', null, null);
}

//ajax for sending messages
function sendMessage() {
    var teamId = $('#mail_to').val();
    var message = $('#mail_message').val();
    if (teamId != "null" && message != null) {
        var data = "toTeam=" + teamId + "&message=" + message + "&message_type=" + 1;
        ajaxRequest('GET', 'pages/ajax_send_message.jsp', data, 'mail_sent', null, mailboxRefresh);

    } else {
        $('.notif_message').show();
        $('#mail_sent').html("<span class='unsuccessful'>One of the fields is empty</span>");
    }
}

function sendNews() {
    var teamId = $('#news_to').val();
    var message = $('#news_message').val();
    if (teamId != "null" && message != null) {
        var data = "toTeam=" + teamId + "&message=" + message + "&message_type=" + 0;
        ajaxRequest('GET', 'pages/ajax_send_message.jsp', data, 'news_sent', null, newsRefresh);
    } else {
        $('.notif_message').show();
        $('#news_sent').html("<span class='unsuccessful'>One of the fields is empty</span>");
    }
}


function mailboxActions() {
    var data = "";
    ajaxRequest('GET', 'pages/ajax_get_message.jsp', data, 'mail_inbox_container', null, null);
    setInterval(function () {
        ajaxRequest('GET', 'pages/ajax_get_message.jsp', data, 'mail_inbox_container', true, null);
    }, 60000);
}

function mailSentActions() {
    var data = "";
    ajaxRequest('GET', 'pages/ajax_sent_messages.jsp', data, 'mail_sent_container', null, null);
    setInterval(function () {
        ajaxRequest('GET', 'pages/ajax_sent_messages.jsp', data, 'mail_sent_container', true, null);
    }, 60000);
}

function newsActions() {
    var data = "";
    ajaxRequest('GET', 'pages/ajax_get_news.jsp', data, 'news_inbox_container', null, null);
    setInterval(function () {
        ajaxRequest('GET', 'pages/ajax_get_news.jsp', data, 'news_inbox_container', true, null);
    }, 60000);
}

function mailboxRefresh() {
    var data = "";
    ajaxRequest('GET', 'pages/ajax_get_message.jsp', data, 'mail_inbox_container', null, null);
}

function newsRefresh() {
    var data = "";
    ajaxRequest('GET', 'pages/ajax_get_news.jsp', data, 'news_inbox_container', null, null);
}


function check_availability(inputString, inputString2, availabilityHandlingLink) {
    if (inputString.length > 0) {
        $('#Loading').show();
        $.post(availabilityHandlingLink,
            {
                inputString: "" + inputString + "",
                inputString2: "" + inputString2 + ""
            },
            function (data) {
                $('#Info').fadeOut();
                $('#Loading').hide();
                setTimeout("finishAjax('Info', '" + escape(data) + "')", 450);
            });
        return false;
    }
}

function generateGraphData(seriesAll) {


}

function finishAjax(id, data) {


    var check = unescape(data);
    if (check == 0) {
        $('#' + id).html("This value is already in use.Please enter some other value...");
    } else {
        $('#' + id).html("The value is available to use.");
    }
    $('#' + id).fadeIn(1000);
}

//type is either GET or POST
//url is the url of the jsp with from which the fetch is happening
//data is the parameters that are sent to the jsp page. They are separated by '&' and parameters and values are expressed as parameter=value  
//  example for data -- para1=val1&para2=val1&
// noLoader determines if the "loading..." progress is shown or not. Its either set to null, which means a loading... message will be displayed or true if the loading... message is not supposed to be displayed
// returnFunction
function ajaxRequest(type, url, data, returnTo, noLoader, returnFunction) {
    if (type != null && url != null && data != null && returnTo != null) {
        $('#' + returnTo).show();
        if (noLoader == null)
            $('#' + returnTo).html("<div class='loading'>Working...</div>");
        url = url + '?' + data;
        $.ajax({
            type: type,
            url: url,
            success: function (result) {
                $('#' + returnTo).html(result);
                if (returnFunction != null) {
                    returnFunction();
                }
            }
        });
    }
}