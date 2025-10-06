---
title: 404
# from commit 6b43420c664fe5de1a4bd998c37186972d587561
date: 2017-05-20 16:06:00
permalink: /404.html
comments: false
---
<!-- https://codepen.io/akashrajendra/pen/JKKRvQ -->
<style>

    #fof-container {
        display: table;
        width: 100%;
        height: 75vh;
        text-align: center;
    }

    .fof {
        display: table-cell;
        vertical-align: middle;
    }

    .fof h1 {
        font-size: 50px;
        display: inline-block;
        padding-right: 12px;
        animation: type .5s alternate infinite;
    }

    .fof a {
        color: inherit;
    }

    .fof a:visited {
        color: inherit;
    }

    .fof a:hover,
    .fof a:focus {
        color: inherit;
        opacity: 0.8;
    }

    @keyframes type {
        from {
            box-shadow: inset -3px 0px 0px #888;
        }

        to {
            box-shadow: inset -3px 0px 0px transparent;
        }
    }
</style>

<div id="fof-container">
    <div class="fof">
        <h1>Error 404</h1>
        <br />
        <a href="/">回到我的主页</a>
    </div>
</div>
