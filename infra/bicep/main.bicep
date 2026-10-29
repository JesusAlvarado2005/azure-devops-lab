@description('Regione Azure nella quale creare lo Storage Account.')
param location string = resourceGroup().location

@description('Nome globalmente univoco dello Storage Account.')
@minLength(3)
@maxLength(24)
param storageName string

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location

  sku: {
    name: 'Standard_LRS'
  }

  kind: 'StorageV2'

  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }

  tags: {
    Course: 'AZ104'
    UD: '12'
    ManagedBy: 'Bicep'
  }
}

output storageAccountName string = storage.name
output blobEndpoint string = storage.properties.primaryEndpoints.blob
