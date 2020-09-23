# Simple CHAT API with django rest framework

In this API you can create and manage different topics. Also you can create messages, but messages muste be assigned to a topic. You can manage messages from two different endpoints. Endpoint /topics/topic_id/messages/ is connected  to specific topic and from this endpoint you can do CRUD operations only on messages from this topic.

### ENDPOINTS
| ENDPOINT | DESC |
| ------ | ------ |
| /topics/ | CRUD for topics |
| /messages/ | CRUD for messages |
| /topics/topic_id/messages/ | CRUD for messages from topic_id |