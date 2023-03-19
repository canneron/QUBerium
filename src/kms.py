import json
import boto3

# Class holding the AWS Key Management Service client and it's functions
# The AWS KMS holds a symmetric key that admin nodes can use to encrypt and decrpyt student records to obfiscate them
class KMS:
    def __init__(self):
        # Read in config file with AWS credentials
        self.awsDetails = self.readFile()
        self.kmsAccessKey = self.awsDetails['awsKey']
        self.kmsSecretAccessKey = self.awsDetails['awsSecretAccessKey']
        self.keyARN = self.awsDetails['awsARN']
        self.arnRegion = self.awsDetails['arnRegion']
        # Create a KMS client using boto3 libraries to connect to AWS
        self.kms = self.createKMSClient()
        
    def readFile(self, fname=r'C:\Users\Cameron\Documents\csc4006QUBerium\quberium\src\awskms.json'):
        file = None
        with open(fname) as f:
            file = json.load(f)
        return file

    def createKMSClient(self):
        return boto3.client('kms',
                            region_name=self.arnRegion,
                            aws_access_key_id=self.kmsAccessKey,
                            aws_secret_access_key=self.kmsSecretAccessKey)

    # Encrypt the data
    def encrypt(self, data):
        cipher_text = self.kms.encrypt(
            KeyId=self.keyARN,
            Plaintext=json.dumps(data),
            EncryptionAlgorithm='SYMMETRIC_DEFAULT'
        )['CiphertextBlob']
        return cipher_text

    # Decrypt data and return as a JSON
    def decrypt(self, data):
        text = self.kms.decrypt(
            KeyId=self.keyARN,
            CiphertextBlob=data,
            EncryptionAlgorithm='SYMMETRIC_DEFAULT'
        )['Plaintext']
        return json.loads(text)

    