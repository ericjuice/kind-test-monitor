package file_uploader

import (
	"context"
	"fmt"
	"os"
	"strings"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type FileUploader struct {
	srcFilePath      string
	dbAddress        string
	dbUsername       string
	dbPassword       string
	dbName           string
	dbCollectionName string
	hostName         string
}

func (f *FileUploader) init(srcFilePath, dbAddress, dbUsername, dbPassword, dbName, dbCollectionName string, hostName string) {
	f.srcFilePath = srcFilePath
	f.dbAddress = dbAddress
	f.dbUsername = dbUsername
	f.dbPassword = dbPassword
	f.dbName = dbName
	f.dbCollectionName = dbCollectionName
	f.hostName = hostName
}

func (f *FileUploader) uploadFileToMongoDB() int {
	// check file type
	if !strings.HasSuffix(f.srcFilePath, ".stack") {
		return -1
	}

	// read
	fileContent, err := os.ReadFile(f.srcFilePath)
	if err != nil {
		fmt.Println("Failed to read file:", err)
		return -1
	}

	// mongodb client
	clientOptions := options.Client().ApplyURI(f.dbAddress).SetAuth(options.Credential{
		Username: f.dbUsername,
		Password: f.dbPassword,
	})
	client, err := mongo.Connect(context.Background(), clientOptions)
	if err != nil {
		fmt.Println("Failed to connect to MongoDB:", err)
		return -1
	}
	defer client.Disconnect(context.Background())

	// select database and collection
	db := client.Database(f.dbName)
	collection := db.Collection(f.dbCollectionName)

	// insert
	_, err = collection.InsertOne(context.Background(), bson.M{"content": fileContent, "hostName": f.hostName})
	if err != nil {
		fmt.Println("Failed to insert file into MongoDB:", err)
		return -1
	}

	return 1
}

func (f *FileUploader) InsertFile2DB(srcFilePath, dbAddress, dbUsername, dbPassword, dbName, dbCollectionName string, hostName string) int {
	f.init(srcFilePath, dbAddress, dbUsername, dbPassword, dbName, dbCollectionName, hostName)
	return f.uploadFileToMongoDB()
}
