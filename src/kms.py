import json
import boto3

class KMS:

    def __init__(self):
        self.awsDetails = self.readFile()
        self.kmsAccessKey = self.awsDetails['awsKey']
        self.kmsSecretAccessKey = self.awsDetails['awsSecretAccessKey']
        self.keyARN = self.awsDetails['awsARN']
        self.arnRegion = self.awsDetails['arnRegion']
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

    
    def encrypt(self, secret_text):
        cipher_text = self.kms.encrypt(
            KeyId=self.aws_kms_arn,
            Plaintext=secret_text.encode(),
            EncryptionAlgorithm='SYMMETRIC_DEFAULT'
        )['CiphertextBlob']
        return cipher_text


    def decrypt(self, cipher_text):
        text = self.kms.decrypt(
            KeyId=self.aws_kms_arn,
            CiphertextBlob=cipher_text,
            EncryptionAlgorithm='SYMMETRIC_DEFAULT'
        )['Plaintext']
        return text.decode()

    