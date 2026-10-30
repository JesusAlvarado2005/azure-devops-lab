param location string = resourceGroup().location

var acrName = 'acrud1315${uniqueString(resourceGroup().id)}'

resource registry 'Microsoft.ContainerRegistry/registries@2025-11-01' = {
  name: acrName
  location: location

  sku: {
    name: 'Basic'
  }

  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'

    // UD14 e UD15 usano ruoli ACR classici (AcrPull/AcrPush).
    // La modalità viene fissata esplicitamente per non dipendere dal default del servizio.
    roleAssignmentMode: 'LegacyRegistryPermissions'
  }

  tags: {
    Course: 'AZ104'
    Purpose: 'FinalDelivery'
    ManagedBy: 'Bicep'
  }
}

output acrName string = registry.name
output acrLoginServer string = registry.properties.loginServer
