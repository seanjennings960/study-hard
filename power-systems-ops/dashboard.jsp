<!DOCTYPE html>















<html>

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>Player - Electricity Market</title>
    <link rel="stylesheet" type="text/css" href="../styles/main.css"/>
    <link rel="stylesheet" type="text/css" href="../styles/newstyle.css"/>
    <link rel="stylesheet" type="text/css" href="../styles/flexipagestyle.css"/>
    <script type="text/javascript" src="../scripts/jquery-1.6.min.js"></script>
    <script type="text/javascript" src="../scripts/jquery.tablednd_0_5.js"></script>
    <script type="text/javascript" src="../scripts/jquery.flot.js"></script>
    <script type="text/javascript" src="../scripts/jquery.flot.stack.js"></script>
    <script type="text/javascript" src="../scripts/main.js"></script>
    <script type="text/javascript" src="../scripts/player.js"></script>
    <script type="text/javascript" src="../scripts/jquery.flot.axislabels.js"></script>
    <script type="text/javascript" src="../scripts/jquery.flot.text.js"></script>
    <script type="text/javascript" src="../scripts/canvas2image.js"></script>
    <script type="text/javascript" src="../scripts/base64.js"></script>
    <script type="text/javascript" src="../scripts/jquery.validate.js"></script>
    <script type="text/javascript" src="../scripts/highcharts.js"></script>
    <script type="text/javascript" src="../scripts/exporting.js"></script>
    <script type="text/javascript" src="../scripts/highcharts-more.js"></script>
</head>


<body>
<div id="outer">

    <div id="header">
        <div id="headerlogo">
            <span class="headerlogo"><img src="../images/emg.png" alt="EMG" height="70" width="123"/></span>
            <span class="headerround">Round 4</span>
        </div>

        <div id="headeravatar"><img src="../images/avatar.png" alt="avatar" height="100" width="101"/></div>
        <div id="headermission">
            <p><span class="companyname">ConEd</span></p>
            <span class="playerheaderinstance">Etopia</span>
            <div id="mission">
                <span id="message_length"></span>
                
                <h6 style="color: white;" id='mission_h6'>Set your mission statement--Max of 100 characters
                    <span>Edit</span></h6>
                
            </div>
        </div>
        <div id="headerempty"></div>
        <div id="headericon"><img src="../images/dashboard.png" alt="Dashboard" height="140" width="140"/></div>
        <div id="headerbar">
            <div id="littleicons">
                <a href="../instance_select.jsp" title="Other instances"><img src="../images/other_instances-tn.png"
                                                                              alt="Settings" height="20px"
                                                                              width="20px"/></a>
                <a href="../logout.jsp" title="Logout"><img src="../images/logout-tn.png" alt="Logout" height="20px"
                                                            width="20px"/></a>
            </div>
            <div class="iconindent1">
                <a href="dashboard.jsp" title="Dashboard"><img src="../images/dashboard-tn.png" alt="Dashboard"
                                                               height="40px" width="40px"/></a>
                <a href="stocks_and_trends.jsp" title="Stocks & trends"><img src="../images/stocks_trends-tn.png"
                                                                             alt="Stocks & trends" height="40px"
                                                                             width="40px"/></a>
            </div>
            <div class="iconindent">
                <a href="plantsOverview.jsp" title="Power plants"><img src="../images/power_plants-tn.png"
                                                                       alt="Power plants" height="40px"
                                                                       width="40px"/></a>
                <a href="plantsAuctioning.jsp" title="Build, decommision or trade plant"><img
                        src="../images/investments-tn.png" alt="Build, decommision or trade plant" height="40px"
                        width="40px"/></a>
                <a href="bank.jsp" title="Bank account"><img src="../images/bank-tn.png" alt="Bank account"
                                                             height="40px" width="40px"/></a>
            </div>
            <div class="iconindent">
                <a href="electricity_market.jsp" title="Electricity market"><img
                        src="../images/electricity_market-tn.png" alt="Electricity market" height="40px" width="40px"/></a>
                
                
                <a href="balancing_market.jsp" title="Balancing market"><img src="../images/balance-tn.png"
                                                                             alt="Balancing market" height="40px"
                                                                             width="40px"/></a>
                <div id="place_bids_new" title="Place bids">
                    <img src="../images/place_bids-tn.png" alt="Place bids" height="40px" width="40px"/>
                </div>
            </div>
            <!--<div class="iconindent">
                <a href="" title="News"><img src="../images/news-tn.png" alt="News" height="40px" width="40px" /></a>
                <a href="" title="Mail"><img src="../images/mail-tn.png" alt="Mail" height="40px" width="40px" /></a>
            </div>-->
            <div id="headericonname">
                <h2>Dashboard</h2>
            </div>
        </div>
    </div>

    <div id="newcontent">
        <div class="article">


            <div class="component graph left white">
                













<script type="text/javascript">

    $(function () {
        $('#bankbalance').highcharts({
            chart: {
                type: 'line'
            },
            title: {
                text: 'Company bank balances'
            },
            xAxis: {
                title: {
                    text: 'Round'
                },
            },
            yAxis: {
                min: null,
                title: {
                    text: 'IBank balance (M€)'
                },
                stackLabels: {
                    enabled: true,
                    style: {
                        fontWeight: 'bold',
                        color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                    }
                }
            },
            legend: {
                align: 'left',
                x: 60,
                verticalAlign: 'top',
                y: 30,
                floating: true,
                backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
                borderColor: '#CCC',
                borderWidth: 1,
                layout: 'vertical'
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.x + '</b><br/>' +
                        this.series.name + ': ' + this.y + '<br/>' +
                        'Total: ' + this.point.stackTotal;
                }
            },
            plotOptions: {
                column: {
                    stacking: 'normal',
                    dataLabels: {
                        enabled: true,
                        color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                        style: {
                            textShadow: '0 0 3px black, 0 0 3px black'
                        }
                    }
                }
            },
            series: [{name:'Xcel',data:[[1,2588.524346990568],[2,2349.3309945493043],[3,1608.8302342122859]]}, {name:'Duke Energy',data:[[1,2568.376762335616],[2,2079.846748134058],[3,1533.9590236791373]]}, {name:'AES',data:[[1,2390.8918375138924],[2,2513.6798568069275],[3,1854.3990622745075]]}, {name:'Dominion',data:[[1,904.7731547782679],[2,582.0177613547131],[3,-378.530987435212]]}, {name:'ConEd',data:[[1,2569.114741595916],[2,2481.304672075071],[3,1968.1879006350712]]}]
        });
    });

</script>
<div id="bankbalance" class="new-graph-container">
</div>

            </div>
            <div class="component graph left white">
                



















<div id="market_price_graph" class="new-graph-container">
</div>
<script type="text/javascript">
    $(function () {
        var chart;
        var series1 = {
            name: "Peak",
            data:[[1,47.0],[2,227.18500000000003],[3,36.5]],
            color: "#C31111",
        };
        var series2 = {
            name: "Off-peak",
            data:[[1,26.2],[2,42.678],[3,19.87]],
            color: "#389ADB",
        };

        var series3 = {
            name: "Shoulder",
            data:[[1,30.42],[2,61.0],[3,28.6]],
            color: "#E9DA0A",
        };
        chart = new Highcharts.Chart({
            chart: {
                renderTo: 'market_price_graph',
                type: 'line'
            },
            title: {
                text: 'Electricity prices'
            },
            xAxis: {
                tickmarkPlacement: 'on',
                title: {
                    text: 'Round'
                }
            },
            yAxis: {
                title: {
                    text: 'Price (€/MWh)'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            legend: {
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top',
                x: 60,
                y: 30,
                floating: true,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                borderWidth: 0
            },
            series: [series1, series2, series3]
        });
    });

</script>


            </div>
            <div class="component graph left white">
                















<div id="market_demand_graph" class="graph-container">
</div>

<script type="text/javascript">
    $(function () {
        var chart;
        var series1 = {
            name: "Peak",
            data:[[1,12530.0],[2,10940.05],[3,13011.123916999999]],
            color: "#C31111"
        };
        var series2 = {
            name: "Off-peak",
            data:[[1,8738.0],[2,8719.92],[3,9061.693481]],
            color: "#389ADB"
        };

        var series3 = {
            name: "Shoulder",
            data:[[1,10695.8],[2,10569.3],[3,11032.258698999998]],
            color: "#E9DA0A"
        };
        chart = new Highcharts.Chart({
            chart: {
                renderTo: 'market_demand_graph',
                type: 'line'
            },
            title: {
                text: 'Electricity consumption'
            },
            xAxis: {
                tickmarkPlacement: 'on',
                title: {
                    text: 'Round'
                }
            },
            yAxis: {
                title: {
                    text: 'Volume (MW)'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            legend: {
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top',
                x: 60,
                y: 30,
                floating: true,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                borderWidth: 0
            },
            series: [series1, series2, series3]
        });
    });

</script>

            </div>

            
            <div class="component graph left white">
                













<!--<h4>Your current electricity bids</h4>-->



<div id="bidding_behav_graph" class="graph-container">

</div>
<script type="text/javascript">
    $(function () {
        var chart;
        var series1 = {
            name: "Peak hours",
            data:[[0.0,0.0]],
            color: "#6A287E",
            step: 'left'
        };

        var series2 = {
            name: "Off-peak hours",
            data:[[0.0,0.0]],
            color: "#7E2217",
            step: 'left'
        };

        var series3 = {
            name: "Shoulder hours",
            data:[[0.0,0.0]],
            color: "#2B60DE",
            step: 'left'
        };


        chart = new Highcharts.Chart({
            chart: {
                renderTo: 'bidding_behav_graph',
                //type: 'line'
            },
            title: {
                text: 'Your electricity bids in this round'
            },
            xAxis: {
                tickmarkPlacement: 'on',
                title: {
                    text: 'Volume (MW)'
                }
            },
            yAxis: {
                title: {
                    text: 'Price (€/MWh)'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            legend: {
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top',
                x: 60,
                y: 30,
                floating: true,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                borderWidth: 0
            },
            series: [series1, series2, series3]
        });

    });


</script>


            </div>
            
            
            <div class="component graph left white">
                














<form method="post">
    <select name="selectedRoundId" id="previous_round_bids_graph" onchange="getPreviousRoundBidsGraph()">
        <option value='5' selected='selected'>Round 3</option><option value='4'>Round 2</option><option value='3'>Round 1</option>
    </select>
</form>




<div id="ajax_previous_round_bids_graph">
    <div id="previous_round_bids" class="graph-container">
        <script type="text/javascript">
            $(function () {
                var chart;
                var series1 = {
                    name: "Peak bids",
                    data:[[0.0,0.0],[87.0,0.0],[116.0,4.904],[916.0,19.87],[1616.0,21.059],[1706.0,37.077],[2306.0,39.204],[2606.0,53.523],[2656.0,55.481],[2706.0,55.481]],
                    color: "#566D7E",
                    step: 'right'
                    /*points: {show: false},
                     lines: {show: true, fill: false, steps: true},
                     bars: {show: false},
                     yaxis: 1*/
                };
                var series2 = {
                    name: "Peak price",
                    data:[[0,36.5],[2706.0,36.5]],
                    color: "#2B60DE",
                    type: 'line'
                };
                var series3 = {
                    name: "Off-peak bids",
                    data:[[0.0,0.0],[87.0,0.0],[116.0,4.904],[916.0,19.87],[1616.0,21.059],[1706.0,37.077],[2306.0,39.204],[2606.0,53.523],[2656.0,55.481],[2706.0,55.481]],
                    color: "#AA6464",
                    step: 'right'
                };
                var series4 = {
                    name: "Off-peak price",
                    data:[[0,19.87],[2706.0,19.87]],
                    color: "#66AEA9",
                    type: 'line'
                };
                var series5 = {
                    name: "Shoulder bids",
                    data:[[0.0,0.0],[87.0,0.0],[116.0,4.904],[916.0,19.87],[1616.0,21.059],[1706.0,37.077],[2306.0,39.204],[2606.0,53.523],[2656.0,55.481],[2706.0,55.481]],
                    color: "#2C6B45",
                    step: 'right'
                };
                var series6 = {
                    name: "Shoulder price",
                    data:[[0,28.6],[2706.0,28.6]],
                    color: "#AEA834",
                    type: 'line'
                };
                chart = new Highcharts.Chart({
                    chart: {
                        renderTo: 'previous_round_bids'
                    },
                    title: {
                        text: 'Your previous electricity bids'
                    },
                    xAxis: {
                        tickmarkPlacement: 'on',
                        title: {
                            text: 'Volume (MW)'
                        }
                    },
                    yAxis: {
                        title: {
                            text: 'Price (€/MWh)'
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    legend: {
                        layout: 'horizontal',
                        align: 'left',
                        verticalAlign: 'bottom',
                        x: 10,
                        y: 10,
                        floating: true,
                        itemStyle: {
                            fontSize: '10px'
                        },
                        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                        borderWidth: 0
                    },
                    series: [series1, series5, series3, series2, series6, series4]
                });
            });


            
        </script>
    </div>
    
</div>
 
            </div>
            <div class="clear"></div>
            <div class="component table left white">
                











<h4>Available and traded capacity</h4>

<div id="electricity_sold_imbalance">
    <table>
        <thead>
        <tr>
            <th>Period</th>
            <th></th>
            <th colspan="3" align="left" class="left-line">Off-peak hours</th>
            <th colspan="3" align="left" class="left-line">Shoulder hours</th>
            <th colspan="3" align="left" class="left-line">Peak hours</th>
        </tr>
        <tr>
            <th>Round</th>
            <th>Available capacity (MW)</th>
            
            <th class="left-line">Sold in spot (MW)</th>
            <th>Sold in balancing (MW)</th>
            <th>Purchased in balancing (MW)</th>
            
            <th class="left-line">Sold in spot (MW)</th>
            <th>Sold in balancing (MW)</th>
            <th>Purchased in balancing (MW)</th>
            
            <th class="left-line">Sold in spot (MW)</th>
            <th>Sold in balancing (MW)</th>
            <th>Purchased in balancing (MW)</th>
            
        </tr>
        </thead>
        <tbody>
        
        <tr>
            <td class="center-align">3
            </td>
            <td class="right-align">2706.00
            </td>
            <td class="right-align left-line">1357.89
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
            <td class="right-align left-line">1706.00
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
            <td class="right-align left-line">1706.00
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
        </tr>
        
        <tr>
            <td class="center-align">2
            </td>
            <td class="right-align">2028.40
            </td>
            <td class="right-align left-line">1928.00
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
            <td class="right-align left-line">2028.40
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
            <td class="right-align left-line">2028.40
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
        </tr>
        
        <tr>
            <td class="center-align">1
            </td>
            <td class="right-align">2581.20
            </td>
            <td class="right-align left-line">1631.00
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
            <td class="right-align left-line">1813.85
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
            <td class="right-align left-line">2581.20
            </td>
            <td class="right-align">0.00
            </td>
            
            <td class="right-align">0.00
            </td>
            
        </tr>
        
        </tbody>
    </table>
</div>
            </div>
            <div class="component table left white">
                












<h4>Mission statements</h4>

<div id="view_team_mission_statements">
    <table>
        <thead>
        <tr>
            <th>Team</th>
            <th>Mission statement</th>
        </tr>
        </thead>
        <tbody>
        
        <tr>
            <td>Dominion
            </td>
            
            <td>--</td>
            
        </tr>
        
        <tr>
            <td>AES
            </td>
            
            <td>--</td>
            
        </tr>
        
        <tr>
            <td>Duke Energy
            </td>
            
            <td>--</td>
            
        </tr>
        
        <tr>
            <td>ConEd
            </td>
            
            <td>--</td>
            
        </tr>
        
        <tr>
            <td>Xcel
            </td>
            
            <td>--</td>
            
        </tr>
        
        </tbody>
    </table>
</div>

            </div>
        </div>
    </div>
    <div class="clear"></div>
    









<div id="hidden_boxes">
    <div id="mailbox_container" class="hidden_box">
        <span class="close_hidden_container">Close</span>
        <ul id="mailbox_nav">
            <li id="mail_inbox" class="active">Inbox</li>
            
            <li id="compose_mail">Compose</li>
        </ul>
        <div id="mail_inbox_container" class="mailbox_content">
        </div>
        
        <div id="compose_mail_container" class="mailbox_content">
            <div class="notif_message" id="mail_sent">
            </div>
            <label>To <br/><select id="mail_to">
                <option value="null">...</option>
                
                <option value="6">Xcel
                </option>
                
                <option value="7">Duke Energy
                </option>
                
                <option value="8">AES
                </option>
                
                <option value="9">Dominion
                </option>
                
                <option value="10">ConEd
                </option>
                
                <option value="3">Operator</option>
                <option value="999">Send to all teams</option>
            </select></label><br/>
            <label>
                Message <br/><textarea id="mail_message"></textarea>
            </label><br/>
            <input type="button" id="message_send" value="Send"/>
        </div>
    </div>
    <div id="mailbox_sent_container" class="hidden_box">
        <span class="close_hidden_container">Close</span>
        <ul id="mailbox_nav">
            <li id="mail_sent_to" class="active">Sent</li>
        </ul>
        <div id="mail_sent_container" class="mailbox_content">
        </div>
    </div>
    <div id="news_full_container" class="hidden_box">
        <span class="close_hidden_container">Close</span>
        <h3 class="titles" id="news_title">News</h3>
        <div id="news_inbox_container" class="mailbox_content">

        </div>
    </div>
    <div id="bids_container" class="hidden_box">
        <span class="close_hidden_container">Close</span>
        <ul id="bidbox_nav">
            <li id="electricity_bidbox_li" class="active">Electricity</li>
            
        </ul>
        <div id="bids_submit_results"></div>
        <div id="bidbox_splash" class="bidbox_boxes">

        </div>
        <div id="bidbox_electricity" class="bidbox_boxes">
            
<script type="text/javascript">
    $(document).ready(function () {
        var fields = $("#submit_ebids.eBidsInputParams input[type=text]");
        fields.blur(function () {
            if (this.value === "") {
                $(this).next("span").text("");
                //var spanValue=$(this).next("span").text();
                $(this).next("span").append("enter value");
                $(this).next("span").show();
            } else if (this.value !== "") {
                //check for numbers
                if (this.value.match(/^(?:\d*\.\d{1,9}.\d{-1,-9}|\d+)$/)) {
                    $(this).next("span").text("");
                    $(this).next("span").hide();
                } else {
                    if (($(this).next("span").text()) !== "") {
                        if (this.value.match(/^[A-Za-z_]*[A-Za-z][A-Za-z_]*$/)) {
                            $(this).next("span").text("");
                            $(this).next("span").append("no strings");
                            $(this).next("span").show();
                        } else {
                            $(this).next("span").text("");
                            $(this).next("span").append("only 9 decimal points");
                            $(this).next("span").show();
                        }
                    }

                }
            }
        });

    });

</script>

<div id="ajax_electricity_bids">
    <div class="bidbox_extra">
        <strong>Download the template Excel file here.</strong>
        <iframe src="pages/download_ebids_template.jsp" frameborder=0 scrolling="no" width="100" height="30"
                marginwidth="0px"></iframe>
        <!--<p<font style="color: #06484f;  font-size: 15px">You can either fill the bid form directly below or download a template here, fill up data and upload it to fill the tables up from the file.</font></p>
        <p><font style="color: #06484f; font-size: 15px">There are three segments: one with 5000 off-peak hours, one with 3600 shoulder hours and one with 160 peak hours.</font></p>-->
        <b><font style="color: #06484f; font-size: 15px">Choose -- Upload -- Submit</font></b>
        <iframe src="pages/upload_form_electricity_bids.jsp" frameborder=0 scrolling="no"></iframe>
        <input type="button" onclick="parse_excel_ebids()" value="Submit"/>
        <!--<input type="button" value="Submit bids" onclick="processBids('electricity')" id="submit" />-->
    </div>


    <!--    <form name="submit_ebids" id="submit_ebids" class="eBidsInputParams">

        <table>
            <thead>
                <tr>
                    <th colspan="2" class="hours_divider">Off-peak hours</th>
                    <th colspan="2" class="hours_divider">Shoulder hours</th>
                    <th colspan="2" class="hours_divider">Peak hours</th>

                </tr>
                <tr>
                    <th>Volume (MW)</th>
                    <th>Price (&euro;/MWh)</th>
                    <th>Volume (MW)</th>
                    <th>Price (&euro;/MWh)</th>
                    <th>Volume (MW)</th>
                    <th>Price (&euro;/MWh)</th>
                </tr>
            </thead>
            <tbody>
                <tr>

                    <td>
                        <input type="text" name="volume_op,0" id="volume_op,0" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,0" id="price_op,0" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,0" id="volume_s,0" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,0" id="price_s,0" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,0" id="volume_p,0" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,0" id="price_p,0" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                </tr>
                <tr>

                    <td>
                        <input type="text" name="volume_op,1" id="volume_op,1" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,1" id="price_op,1" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,1" id="volume_s,1" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,1" id="price_s,1" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,1" id="volume_p,1" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,1" id="price_p,1" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,2" id="volume_op,2" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,2" id="price_op,2" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,2" id="volume_s,2" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,2" id="price_s,2" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,2" id="volume_p,2" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,2" id="price_p,2" value="0.0"  />
                        <span style="color:red"></span>
                    </td>

                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,3" id="volume_op,3" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,3" id="price_op,3" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,3" id="volume_s,3" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,3" id="price_s,3" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,3" id="volume_p,3" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,3" id="price_p,3" value="0.0"  />
                        <span style="color:red"></span>
                    </td>

                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,4" id="volume_op,4" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,4" id="price_op,4" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,4" id="volume_s,4" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,4" id="price_s,4" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,4" id="volume_p,4" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,4" id="price_p,4" value="0.0"  />
                        <span style="color:red"></span>
                    </td>

                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,5" id="volume_op,5" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,5" id="price_op,5" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,5" id="volume_s,5" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,5" id="price_s,5" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,5" id="volume_p,5" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,5" id="price_p,5" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    
                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,6" id="volume_op,6" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,6" id="price_op,6" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,6" id="volume_s,6" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,6" id="price_s,6" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,6" id="volume_p,6" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,6" id="price_p,6" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    
                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,7" id="volume_op,7" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,7" id="price_op,7" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,7" id="volume_s,7" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,7" id="price_s,7" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,7" id="volume_p,7" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,7" id="price_p,7" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    
                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,8" id="volume_op,8" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,8" id="price_op,8" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,8" id="volume_s,8" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,8" id="price_s,8" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,8" id="volume_p,8" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,8" id="price_p,8" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    
                </tr>
                <tr>

                    <td>
                        <input type="text" name="volume_op,9" id="volume_op,9" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,9" id="price_op,9" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,9" id="volume_s,9" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,9" id="price_s,9" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,9" id="volume_p,9" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,9" id="price_p,9" value="0.0"  />
                        <span style="color:red"></span>
                    </td>                    
                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,10" id="volume_op,10" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,10" id="price_op,10" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,10" id="volume_s,10" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,10" id="price_s,10" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,10" id="volume_p,10" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,10" id="price_p,10" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    
                </tr>
                <tr>

                    <td>
                        <input type="text" name="volume_op,11" id="volume_op,11" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,11" id="price_op,11" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,11" id="volume_s,11" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,11" id="price_s,11" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,11" id="volume_p,11" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,11" id="price_p,11" value="0.0"  />
                        <span style="color:red"></span>
                    </td>                    
                </tr>
                <tr>

                    <td>
                        <input type="text" name="volume_op,12" id="volume_op,12" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,12" id="price_op,12" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,12" id="volume_s,12" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,12" id="price_s,12" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,12" id="volume_p,12" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,12" id="price_p,12" value="0.0"  />
                        <span style="color:red"></span>
                    </td>                    
                </tr>
                <tr>
                    <td>
                        <input type="text" name="volume_op,13" id="volume_op,13" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,13" id="price_op,13" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,13" id="volume_s,13" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,13" id="price_s,13" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,13" id="volume_p,13" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,13" id="price_p,13" value="0.0"  />
                        <span style="color:red"></span>
                    </td>                    
                </tr>
                <tr>

                    <td>
                        <input type="text" name="volume_op,14" id="volume_op,14" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_op,14" id="price_op,14" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_s,14" id="volume_s,14" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_s,14" id="price_s,14" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="volume_p,14" id="volume_p,14" value="0.0"  />
                        <span style="color:red"></span>
                    </td>
                    <td>
                        <input type="text" name="price_p,14" id="price_p,14" value="0.0"  />
                        <span style="color:red"></span>
                    </td>                    
                </tr>
            </tbody>

        </table>
        
        
    </form>
-->
</div>
        </div>
        
    </div>
</div>
<div id="footer">
    <p class="center small">&nbsp;
        <a href="" title="Delft University of Technology and Fields of View"><img
                style="float:none; margin:0 auto; display:block" src="../images/logos.png"
                alt="Technische Universiteit Delft en Fields of View" height="28" width="201"/></a></p>
</div>

</div>
</body>
</html>



