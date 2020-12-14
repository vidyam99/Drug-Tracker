pragma solidity ^0.4.24;
import "./Ownable.sol";
import "./ConsumerRole.sol";
import "./DistributorRole.sol";
import "./ManufacturerRole.sol";
import "./RetailerRole.sol"; 

// Define a contract 'Supplychain'
contract SupplyChain is Ownable, ConsumerRole, ManufacturerRole, RetailerRole, DistributorRole {

  // Define a variable called 'upc' for Universal Product Code (UPC) which is Product ID
  uint  upc;

  // Define a public mapping 'items' that maps the UPC to an Item.
  mapping (uint => Item) items;
  // Define a mapping which stores history of the Items Journey
  mapping (uint => mapping (uint => Entry)) itemsHistory;
  uint[] forsale;

  // Define enum 'State' with the following values:
  enum State  {
    Manufactured,  // 0
    Packaged,   // 1
    ForSale,    // 2
    Sold,       // 3
    Shipped,    // 4
    Received,   // 5
    Purchased   // 6
  }

  State constant defaultState = State.Manufactured;

  struct Entry{
      string timestamp;
      State entryState;
      address by;
      uint price;
      string location;
  }

  // Define a struct 'Item' with the following fields:
  struct Item {
    uint    upc;
    string itemType;
    address ownerID;
    address originManufacturerID; 
    string  itemName; // Product Name
    string  productNotes; // Product Notes
    uint    productPrice; // Product Price
    State   itemState;  // Product State as represented in the enum above
    address distributorID;  
    address retailerID; 
    address consumerID;
    uint totalEntry;
  }

  event Manufactured(uint upc);
  event Packaged(uint upc);
  event ForSale(uint upc);
  event Sold(uint upc);
  event Shipped(uint upc);
  event Received(uint upc);
  event Purchased(uint upc);

  // Define a modifer that verifies the Caller
  modifier verifyCaller (address _address) {
    require(msg.sender == _address, "the sender address does not match");
    _;
  }

  // Define a modifier that checks if the paid amount is sufficient to cover the price
  modifier paidEnough(uint _price) {
    require(msg.value >= _price, "insufficient payment");
    _;
  }

  // Define a modifier that checks the price and refunds the remaining balance
  modifier checkValue(uint _upc) {
    _;
    uint _price = items[_upc].productPrice;
    uint amountToReturn = msg.value - _price;
    items[_upc].consumerID.transfer(amountToReturn);
  }


  // Define a modifier that checks if an item.state of a upc is Manufactured
  modifier manufactured(uint _upc) {
    require(items[_upc].itemState == State.Manufactured, "item not manufactured");
    _;
  }

  // Define a modifier that checks if an item.state of a upc is Packed
  modifier packaged(uint _upc) {
    require(items[_upc].itemState == State.Packaged, "item not packaged");
    _;
  }

  // Define a modifier that checks if an item.state of a upc is ForSale
  modifier forSale(uint _upc) {
    require(items[_upc].itemState == State.ForSale, "item not for sale");
    _;
  }

  // Define a modifier that checks if an item.state of a upc is Sold
  modifier sold(uint _upc) {
    require(items[_upc].itemState == State.Sold, "item not sold");
    _;
  }

  // Define a modifier that checks if an item.state of a upc is Shipped
  modifier shipped(uint _upc) {
    require(items[_upc].itemState == State.Shipped, "item not shipped");
    _;
  }

  // Define a modifier that checks if an item.state of a upc is Received
  modifier received(uint _upc) {
    require(items[_upc].itemState == State.Received, "item not received");
    _;
  }

  // Define a modifier that checks if an item.state of a upc is Purchased
  modifier purchased(uint _upc) {
    require(items[_upc].itemState == State.Purchased, "item not purchased");
    _;
  }


  // Define a modifier that checks if the msg.sender can sell the item.
  modifier canSell(uint _upc) {
    require(canAccountSellItem(msg.sender, _upc), "the sender cannot sell the item");
    _;
  }

// Define a modifier that checks if the msg.sender can ship the item
  modifier canShip(uint _upc) {
    require(canAccountShipItem(msg.sender, _upc), "the sender cannot ship the item");
    _;
  }

  // Define a modifier that checks if the msg.sender can buy the item
  modifier canBuy(uint _upc) {
    require(canAccountBuyItem(msg.sender, _upc), "the sender cannot buy the item");
    _;
  }

  // Define a modifier that checks if the msg.sender can package the item
  modifier canPackage(uint _upc) {
    require(canAccountPackageItem(msg.sender, _upc), "the sender cannot package the item");
    _;
  }

  // Define a modifier that checks if the msg.sender can receive the item
  modifier canReceive(uint _upc) {
    require(canAccountReceiveItem(_upc), "the sender cannot receive the item");
    _;
  }

  // In the constructor set 'owner' to the address that instantiated the contract
  constructor() public payable {
    transferOwnership(msg.sender);
    upc = 1;
  }

  // Define a function 'kill' if required
  function kill() public {
    if (msg.sender == owner()) {
      selfdestruct(owner());
    }
  }

  // Define a function 'manufactureItem' that allows a manufacturer to mark an item 'Manufactured'
  function manufactureItem(uint _upc, string _itemType,string _itemName, uint _productPrice, 
    string  _productNotes, string _timestamp, string _location) public
    onlyManufacturer
    {
    // Add the new item as part of the Manufacturing process
    // Add the new item to the inventory and mark it as manufactured.
    items[_upc] = Item(
          {upc: _upc,
          itemType: _itemType,
          ownerID: msg.sender,
          originManufacturerID: msg.sender,
          itemName: _itemName,
          productNotes: _productNotes,
          productPrice: _productPrice,
          itemState: State.Manufactured,
          distributorID: 0,
          retailerID: 0,
          consumerID: 0,
          totalEntry: 1});

    // make an entry in itemsHistory
    Entry memory newEntry = Entry({
        timestamp: _timestamp,
        entryState: State.Manufactured,
        by: msg.sender,
        price: 0,
        location: _location
    });
    itemsHistory[_upc][items[_upc].totalEntry] = newEntry;

    // Emit the appropriate event
    emit Manufactured(_upc);
  }

  // Define a function 'packItem' that allows a manufacturer or distributor to mark an item 'Packed'
  function packageItem(uint _upc, string _timestamp, string _location) public
  // Call modifier to check if upc has passed previous supply chain stage
  canPackage(_upc)
  {
    // Update the appropriate fields
    items[_upc].itemState = State.Packaged;
    items[_upc].totalEntry = items[_upc].totalEntry+1;
    
    //make an Entry in itemsHistory
    Entry memory newEntry = Entry({
    timestamp: _timestamp,
    entryState: State.Packaged,
    by: msg.sender,
    price: 0,
    location: _location
    });

     itemsHistory[_upc][items[_upc].totalEntry] = newEntry;
    // Emit the appropriate event
    emit Packaged(_upc);
  }

  // Define a function 'sellItem' that allows a manufacturer to mark an item 'ForSale'
  function sellItem(uint _upc, string _timestamp, string _location) public
  // Call modifier to check if upc has passed previous supply chain stage and verify caller of this function
  canSell(_upc)
  {
    // Update the appropriate fields
    items[_upc].itemState = State.ForSale;
    items[_upc].totalEntry = items[_upc].totalEntry+1;
    
    // make an entry in itemsHistory
    Entry memory newEntry = Entry({
    timestamp: _timestamp,
    entryState: State.ForSale,
    by: msg.sender,
    price: 0,
    location: _location
    });
    
    forsale.push(_upc);

     itemsHistory[_upc][items[_upc].totalEntry] = newEntry;
    // Emit the appropriate event
    emit ForSale(upc);
  }

  // Define a function 'buyItem' that allows the disributor to mark an item 'Sold'
  // Use the above defined modifiers to check if the item is available for sale, if the buyer has paid enough,
  // and any excess ether sent is refunded back to the buyer
  function buyItem(uint _upc, string _timestamp, string _location) public payable
    // Call modifier to check if upc has passed previous supply chain stage
    canBuy(_upc)
    // Call modifer to check if buyer has paid enough
    paidEnough(items[_upc].productPrice)
    // Call modifer to send any excess ether back to buyer
    checkValue(_upc)
    {
      address buyer = msg.sender;
      uint price = items[_upc].productPrice;

      // Update the appropriate fields - ownerID, distributorID, itemState
      items[_upc].ownerID = buyer;

      if(items[_upc].distributorID == address(0))
        items[_upc].distributorID = buyer;
      else if(items[_upc].retailerID == address(0))
        items[_upc].retailerID = buyer;
      else if(items[_upc].consumerID == address(0))
        items[_upc].consumerID = buyer;

      items[_upc].itemState = State.Sold;
      items[_upc].totalEntry = items[_upc].totalEntry+1;

      // Transfer money to manufacturer
      items[_upc].ownerID.transfer(price);
      
      //make an entry in itemsHistory
      Entry memory newEntry = Entry({
      timestamp: _timestamp,
      entryState: State.Sold,
      by: msg.sender,
      price: msg.value,
      location: _location
      });

       itemsHistory[_upc][items[_upc].totalEntry] = newEntry;

      // emit the appropriate event
      emit Sold(_upc);
  }

  // Define a function 'shipItem' that allows the distributor to mark an item 'Shipped'
  // Use the above modifers to check if the item is sold
  function shipItem(uint _upc, string _timestamp, string _location) public
    // Call modifier to check if upc has passed previous supply chain stage
    canShip(_upc)
  {
      // Update the appropriate fields
      items[_upc].itemState = State.Shipped;
      items[_upc].totalEntry = items[_upc].totalEntry+1;
      
    //   make an Entry in itemsHistory
      Entry memory newEntry = Entry({
      timestamp: _timestamp,
      entryState: State.Shipped,
      by: msg.sender,
      price: 0,
      location: _location
      });

      itemsHistory[_upc][items[_upc].totalEntry] = newEntry;
      // Emit the appropriate event
      emit Shipped(_upc);
  }

  // Define a function 'receiveItem' that allows the retailer to mark an item 'Received'
  // Use the above modifiers to check if the item is shipped
  function receiveItem(uint _upc, string _timestamp, string _location) public
    canReceive(_upc)
    {
    // Update the appropriate fields - ownerID, retailerID, itemState
      items[_upc].itemState = State.Received;

      items[_upc].totalEntry = items[_upc].totalEntry+1;
      
      // make an entry in itemsHistory
      Entry memory newEntry = Entry({
      timestamp: _timestamp,
      entryState: State.Received,
      by: msg.sender,
      price: 0,
      location: _location
      });

      itemsHistory[_upc][items[_upc].totalEntry] = newEntry;

      // Emit the appropriate event
      emit Received(upc);
  }

  // Define a function that determines whether an account can ship the given item.
  function canAccountShipItem(address _account, uint _upc) public view returns (bool) {
    return (isSold(_upc) &&
    ((isManufacturer(_account, _upc) && items[_upc].ownerID == items[_upc].distributorID
      || isDistributor(_account, _upc) && items[_upc].ownerID == items[_upc].retailerID)));
  }

  // Define a function that determines whether an account can package the given item.
  function canAccountPackageItem(address _account, uint _upc) public view returns (bool) {
    return (isManufactured(_upc) && isManufacturer(_account, _upc));
  }

 // Define a function that determines whether an account can receive the given item.
  function canAccountReceiveItem(uint _upc) public view returns (bool) {
    return (isItemOwner(msg.sender, _upc) && isShipped(_upc));
  }

  // Define a function that determines whether an account can sell the given item.
  function canAccountSellItem(address _account, uint _upc) public view returns (bool) {
    return (isItemOwner(_account, _upc) &&
        ((isManufacturer(_account, _upc) && isPackaged(_upc)) ||
        (isDistributor(_account, _upc) && isReceived(_upc)) ||
        (isRetailer(_account, _upc) && isReceived(_upc))));
  }

  // Define a function that determines whether an account can sell the given item.
  function canAccountBuyItem(address _account, uint _upc) public view returns (bool) {
    return (isForSale(_upc) &&
      ((isDistributor(_account) &&
        items[_upc].distributorID == address(0)) ||
          (isRetailer(_account) &&
            items[_upc].distributorID != address(0) &&
            items[_upc].retailerID == address(0)) ||
          (isConsumer(_account) &&
           items[_upc].distributorID != address(0) &&
           items[_upc].retailerID != address(0) &&
           items[_upc].consumerID == address(0))));
  }

  // Define a function that determines whether the item is packaged.
  function isItemOwner(address _account, uint _upc) public view returns (bool) {
    return (items[_upc].ownerID == _account);
  }

  // Define a function that determines whether the item is packaged.
  function isPackaged(uint _upc) public view returns (bool) {
    return (items[_upc].itemState == State.Packaged);
  }

  // Define a function that determines whether the item is sold.
  function isSold(uint _upc) public view returns (bool) {
    return (items[_upc].itemState == State.Sold);
  }

  // Define a function that determines whether the item is shipped.
  function isShipped(uint _upc) public view returns (bool) {
    return (items[_upc].itemState == State.Shipped);
  }

  // Define a function that determines whether the item is for sale.
  function isForSale(uint _upc) public view returns (bool) {
    return (items[_upc].itemState == State.ForSale);
  }

  // Define a function that determines whether the item was received.
  function isReceived(uint _upc) public view returns (bool) {
    return (items[_upc].itemState == State.Received);
  }

  // Define a function that determines whether the item was manufactured.
  function isManufactured(uint _upc) public view returns (bool) {
    return (items[_upc].itemState == State.Manufactured);
  }

  // Define a function that determines whether the given account manufactured the
  // given item.
  function isManufacturer(address _account, uint _upc) internal view returns (bool) {
    return (isManufacturer(_account) && _account == items[_upc].originManufacturerID);
  }

  // Define a function that determines whether the given account is the distributor
  // of the given item.
  function isDistributor(address _account, uint _upc) internal view returns (bool) {
    return (isDistributor(_account) && _account == items[_upc].distributorID);
  }

  // Define a function that determines whether the given account is the retailer
  // of the given item.
  function isRetailer(address _account, uint _upc) internal view returns (bool) {
    return (isRetailer(_account) && _account == items[_upc].retailerID);
  }

  // Define a function that fetches the product details
  function fetchProductDetails(uint _upc) public view returns
  (
    uint    itemUPC,
    string itemType,
    address ownerID,
    address originManufacturerID,
    string  itemName,
    string  productNotes,
    uint productPrice,
    uint itemState,
    address distributorID,
    address retailerID,
    address consumerID,
    uint totalEntry
  )
  {
      itemUPC = items[_upc].upc;
      itemType = items[_upc].itemType;
      ownerID = items[_upc].ownerID;
      originManufacturerID = items[_upc].originManufacturerID;
      itemName = items[_upc].itemName;
      productNotes = items[_upc].productNotes;
      productPrice = items[_upc].productPrice;
      itemState = uint(items[_upc].itemState);
      distributorID = items[_upc].distributorID;
      retailerID = items[_upc].retailerID;
      consumerID = items[_upc].consumerID;
      totalEntry = items[_upc].totalEntry;
      return (itemUPC, itemType, ownerID, originManufacturerID, itemName, productNotes,
      productPrice, itemState, distributorID, retailerID, consumerID, totalEntry);
  }

  // Define a function that fetches the itemsHistory of an Item
  function fetchItemHistory(uint _upc,uint j) public view returns (string)
  {
    string memory output = '';
      output=concat(output, '{ "Timestamp": ');
      output=concat(output,'"');
      output=concat(output, itemsHistory[_upc][j].timestamp);
      output=concat(output,'"');
      output=concat(output, ', ');
      output=concat(output, '"Entry State": ');
      output=concat(output, uint2str(uint(itemsHistory[_upc][j].entryState)));
      output=concat(output, ', ');
      output=concat(output, '"By": ');
      output=concat(output, '"');
      output=concat(output, toAsciiString(itemsHistory[_upc][j].by));
      output=concat(output,'"');
      output=concat(output, ', ');
      output=concat(output, '"Price": ');
      output=concat(output, uint2str(itemsHistory[_upc][j].price));
      output=concat(output, ', ');
      output=concat(output, '"Location": ');
      output=concat(output,'"');
      output=concat(output, itemsHistory[_upc][j].location);
      output=concat(output,'"');
      output=concat(output,'}');
    return output;
  }

    // a function which concatenates two strings
    function concat(string memory _a, string memory _b) public pure returns (string memory) {
        bytes memory bytes_a = bytes(_a);
        bytes memory bytes_b = bytes(_b);
        string memory length_ab = new string(bytes_a.length + bytes_b.length);
        bytes memory bytes_c = bytes(length_ab);
        uint k = 0;
        for (uint i = 0; i < bytes_a.length; i++) bytes_c[k++] = bytes_a[i];
        for (uint j = 0; j < bytes_b.length; j++) bytes_c[k++] = bytes_b[j];
        return string(bytes_c);
    }
    
    // a function which 
    function toAsciiString(address x) public pure returns (string) {
        bytes memory s = new bytes(40);
        for (uint i = 0; i < 20; i++) {
            byte b = byte(uint8(uint(x) / (2**(8*(19 - i)))));
            byte hi = byte(uint8(b) / 16);
            byte lo = byte(uint8(b) - 16 * uint8(hi));
            s[2*i] = char(hi);
            s[2*i+1] = char(lo);            
        }
        return string(s);
    }

    function char(byte b) public pure returns (byte c) {
        if (uint8(b) < 10) return byte(uint8(b) + 0x30);
        else return byte(uint8(b) + 0x57);
    }
    
    function uint2str(uint _i) internal pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint j = _i;
        uint len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint k = len - 1;
        while (_i != 0) {
            bstr[k--] = byte(uint8(48 + _i % 10));
            _i /= 10;
        }
        return string(bstr);
    }
    
    function remove(uint _upc) public {
        uint index=1000000;
        for (uint i = 0; i<forsale.length; i++){
            if(forsale[i]==_upc) {
                index=i;
                break;
            }
        }
        for(uint j=index;j<forsale.length-1;j++) {
            forsale[i]=forsale[i+1];
        }
        forsale.length--;
        return;
    }
    
    function itemsForSale() public view returns (uint[] _items) {
        return forsale;
    }
}
