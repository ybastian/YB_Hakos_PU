# Map of URLs, routes, and templates

<!-- automatisch erzeugt mit docs/dungeon_keeper.py, nicht von Hand bearbeiten -->

| URL | Methoden | Flask routes.py | Endpunkt | HTML Template |
| --- | -------- | --------------- | -------- | ------------- |
| / | GET | main/routes/home.py | main.home | main/templates/home_intern.html<br>main/templates/home.html |
| /about | GET | main/routes/about.py | main.about | main/templates/about.html |
| /account | GET,POST | users/routes.py | users.account | users/templates/account.html |
| /actionhandler | POST | orders/routes/create_order.py | orders.actionhandler | orders/templates/create_order.html |
| /add-row | GET | main/routes/fg_request.py | main.add_row | main/templates/aufnahme_zeile.html |
| /approver | GET | main/routes/approver.py | main.approver | main/templates/approver.html |
| /approver/&lt;int:order_id&gt;/approve | POST | orders/routes/approval.py | orders.approve_order | – |
| /approver/&lt;int:order_id&gt;/reject | GET,POST | orders/routes/reject_order.py | orders.reject_order | orders/templates/reject_order.html |
| /approver/assign_poweruser | POST | orders/routes/approval.py | orders.approver_assign_poweruser | – |
| /approver/assign_poweruser_form | GET | orders/routes/approval.py | orders.approver_assign_poweruser_form | – |
| /faq | GET | main/routes/faq.py | main.faq | main/templates/faq.html |
| /feedback/&lt;int:feedback_id&gt; | GET,POST | orders/routes/feedback.py | orders.observation_feedback | main/templates/observation_feedback.html |
| /feedback/&lt;int:feedback_id&gt;/cancel | POST | orders/routes/feedback.py | orders.cancel_observation_feedback | – |
| /feedback/&lt;int:feedback_id&gt;/edit | GET,POST | orders/routes/feedback.py | orders.edit_observation_feedback | main/templates/observation_feedback.html |
| /fgrequest | GET | main/routes/fg_request.py | main.fgrequest | main/templates/create_obs_request.html |
| /gast | GET | main/routes/gast.py | main.gast | main/templates/gast.html |
| /gast/approve | POST | main/routes/gast.py | main.gast_approve | – |
| /gast/delete | POST | main/routes/gast.py | main.gast_delete | – |
| /home | GET | main/routes/home.py | main.home | main/templates/home_intern.html<br>main/templates/home.html |
| /impressum | GET | main/routes/impressum.py | main.impressum | main/templates/impressum.html |
| /inout/export | POST | inout/routes.py | inout.export_data | – |
| /inout/import | POST | inout/routes.py | inout.import_data | – |
| /login | GET,POST | users/routes.py | users.login | users/templates/login.html |
| /logout | GET | users/routes.py | users.logout | – |
| /obs_requests | GET | orders/routes/obs_request_complete.py | orders.obs_request_complete | orders/templates/obs_request_complete.html |
| /observationlist_complete | GET | main/routes/observation_database.py | main.observation_database | main/templates/observation_database.html |
| /order_history | GET | orders/routes/obs_request_complete.py | orders.order_history | order_history.html (?)<br>main/templates/home.html |
| /orders | GET | orders/routes/order_list.py | orders.show_orders | orders/templates/orders.html |
| /orders/&lt;int:order_id&gt;/copy_order | POST | orders/routes/order_list.py | orders.copy_order | – |
| /orders/&lt;int:order_id&gt;/delete_order | POST | orders/routes/order_list.py | orders.delete_order | – |
| /orders/&lt;int:order_id&gt;/edit | GET,POST | orders/routes/edit_order_pos.py | orders.edit_order_pos | orders/templates/edit_order_pos.html |
| /orders/&lt;int:order_id&gt;/positions | GET | orders/routes/order_positions.py | orders.show_order_positions | orders/templates/order_positions.html |
| /orders/&lt;int:order_id&gt;/reservation.ics | GET | orders/routes/order_positions.py | orders.download_reservation_ical | – |
| /orders/get_filtersets | POST | orders/routes/api.py | orders.get_filtersets | – |
| /orders/get_telescopes/&lt;int:observatory_id&gt; | GET | orders/routes/api.py | orders.get_telescopes | – |
| /orders/show_calendar | GET | orders/routes/calendar.py | orders.show_calendar | – |
| /orders/status | GET | orders/routes/status_flow.py | orders.status_flow | orders/templates/status_flow.html |
| /orders/user_preference | GET | orders/routes/api.py | orders.get_user_preference | – |
| /orders/user_preference | POST | orders/routes/api.py | orders.set_user_preference | – |
| /password_changed | GET | users/routes.py | users.password_changed | users/templates/password_changed.html |
| /post/&lt;int:post_id&gt; | GET | posts/routes.py | posts.post | posts/templates/post.html |
| /post/&lt;int:post_id&gt;/delete | POST | posts/routes.py | posts.delete_post | – |
| /post/&lt;int:post_id&gt;/update | GET,POST | posts/routes.py | posts.update_post | posts/templates/create_post.html |
| /post/new | GET,POST | posts/routes.py | posts.new_post | posts/templates/create_post.html |
| /poweruser | GET,POST | main/routes/poweruser.py | main.poweruser | main/templates/poweruser.html |
| /poweruser/&lt;int:order_id&gt;/pu_accept | POST | orders/routes/approval.py | orders.pu_accept | – |
| /poweruser_order_history | GET | main/routes/poweruser_history.py | main.poweruser_order_history | main/templates/poweruser_history.html |
| /register | GET,POST | users/routes.py | users.register | users/templates/register.html |
| /request_georg | GET | main/routes/request_georg.py | main.request_georg | main/templates/create_request_georg.html |
| /reset_password | GET,POST | users/routes.py | users.reset_request | users/templates/reset_request.html |
| /reset_password/&lt;token&gt; | GET,POST | users/routes.py | users.reset_token | users/templates/reset_token.html |
| /servicerequest | GET | main/routes/service_request.py | main.servicerequest | main/templates/create_service.html |
| /status | GET | main/routes/home.py | main.status | – |
| /user/&lt;string:username&gt; | GET | users/routes.py | users.user_posts | users/templates/user_posts.html |
| /user_order_history | GET | main/routes/order_history.py | main.user_order_history | main/templates/orders_history.html |
