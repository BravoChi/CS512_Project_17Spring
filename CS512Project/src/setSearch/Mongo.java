package setSearch;

import java.util.Collection;
import java.util.Set;

import org.bson.Document;

import com.mongodb.BasicDBObject;
import com.mongodb.BulkWriteOperation;
import com.mongodb.BulkWriteResult;
import com.mongodb.Cursor;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.MongoClient;
import com.mongodb.MongoClientOptions;
import com.mongodb.ParallelScanOptions;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.IndexOptions;

public class Mongo {
	 //MongoClient mongoClient = new MongoClient();
	// or
	private MongoClient mongoClient;
	private MongoDatabase db;
	private MongoCollection collection;
	private String dbName;
//	private String collName;
	private IndexOptions option;
	public Mongo(String dbName){
		MongoClientOptions.Builder builder = new MongoClientOptions.Builder();
		builder.maxConnectionIdleTime(60000);//set the max wait time in (ms)
	    MongoClientOptions opts = builder.build();
		this.mongoClient = new MongoClient("localhost", opts);
		this.dbName = dbName;
		this.db = mongoClient.getDatabase(dbName);  
//		this.collName = null;
		this.collection = null;
		this.option = new IndexOptions();
		this.option.unique(true);
		System.out.println("Connect to database successfully");
	}
	public MongoCollection<Document> getCollection(String name){
		collection = db.getCollection(name);
		return db.getCollection(name);
	}
	public MongoDatabase dbGetter(){
		return db;
	}
	public String buildIndex(String type){
		return "Successfully created Index: " + collection.createIndex(new Document("pmid", 1), option);
		//System.out.println("Successfully created the Index! ");
	}
//	public static void main(String[] args) {
//		// TODO Auto-generated method stub
//		Mongo mongo = new Mongo("TEST01");
//	    MongoCollection<Document> collection = mongo.getCollection("demo02");
//		Document doc = new Document("pmid", 100)
//				.append("Date", null)
//				.append("Title", "abc")
//				.append("Abstract", "adfwf2")
//				.append("Author", "kk")
//				.append("Journal", null)
//				.append("Entities", new Document());
//		collection.insertOne(doc);
//		collection.insertOne(new Document("pmid", 300));
//		collection.insertOne(new Document("pmid", 200));
//		//mongo.buildIndex("pmid");
//		System.out.println(collection.count());
//		System.out.println("Successfully create index: " + mongo.buildIndex("pmid"));
//	}

}

