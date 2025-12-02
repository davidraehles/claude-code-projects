// Mock MCP Server for Knuspr integration
// This script simulates the 'rohlik-mcp-temp' server

const fs = require('fs');

function log(message) {
    // fs.appendFileSync('fake_mcp_server.log', message + '\n');
    process.stderr.write(message + '\n');
}

// Read input from stdin
process.stdin.setEncoding('utf8');

process.stdin.on('data', (chunk) => {
    const lines = chunk.trim().split('\n');
    for (const line of lines) {
        if (!line) continue;
        try {
            const request = JSON.parse(line);
            handleRequest(request);
        } catch (e) {
            log(`Error parsing JSON: ${e.message} - input: ${line}`);
        }
    }
});

function handleRequest(request) {
    if (request.jsonrpc !== '2.0') return;

    const { id, method, params } = request;

    // Handshake
    if (method === 'initialize') {
        respond(id, {
            protocolVersion: '2024-11-05',
            serverInfo: { name: 'fake-knuspr-server', version: '1.0.0' },
            capabilities: { tools: {} }
        });
        return;
    }

    if (method === 'notifications/initialized') {
        // No response needed
        return;
    }

    if (method === 'tools/list') {
         respond(id, {
             tools: [
                 { name: 'search_products', description: 'Search products' },
                 { name: 'create_cart', description: 'Create a cart' },
                 { name: 'get_delivery_slots', description: 'Get delivery slots' },
                 { name: 'select_delivery_slot', description: 'Select delivery slot' },
                 { name: 'get_cart', description: 'Get cart details' },
                 { name: 'get_account_data', description: 'Get account data' }
             ]
         });
         return;
    }

    if (method === 'tools/call') {
        const { name, arguments: args } = params;
        log(`Called tool: ${name} with args: ${JSON.stringify(args)}`);

        let result = {};

        if (name === 'search_products') {
            result = {
                products: [
                    {
                        product_id: `prod_${args.product_name}_1`,
                        name: `Knuspr ${args.product_name}`,
                        quantity: 1,
                        unit: 'pcs',
                        price: 2.99,
                        available: true,
                        category: 'groceries',
                        confidence: 0.95
                    }
                ]
            };
        } else if (name === 'create_cart') {
             const items = args.items.map(item => ({
                 product_id: item.product_id,
                 name: `Product ${item.product_id}`,
                 quantity: item.quantity,
                 unit: item.unit || 'pcs',
                 price: 2.99,
                 available: true,
                 category: 'groceries'
             }));

             result = {
                 cart: {
                     cart_id: `cart-${Date.now()}`,
                     items: items,
                     total_price: items.reduce((sum, item) => sum + (item.price * item.quantity), 0),
                     created_at: new Date().toISOString()
                 }
             };
        } else if (name === 'get_delivery_slots') {
             result = {
                 delivery_slots: [
                     {
                         slot_id: 'slot-1',
                         date: new Date(Date.now() + 86400000).toISOString(),
                         time_window: '08:00-10:00',
                         price: 4.99,
                         available: true
                     }
                 ]
             };
        } else if (name === 'select_delivery_slot') {
             result = { success: true };
        } else if (name === 'get_account_data') {
            result = { user_id: 'user-123', email: 'test@example.com' };
        } else if (name === 'get_cart') {
             result = {
                 cart: {
                     cart_id: args.cart_id,
                     items: [],
                     total_price: 0,
                     created_at: new Date().toISOString()
                 }
             };
        }

        respond(id, {
            content: [{ type: 'text', text: JSON.stringify(result) }],
            isError: false
        });
        return;
    }
}

function respond(id, result) {
    const response = {
        jsonrpc: '2.0',
        id: id,
        result: result
    };
    process.stdout.write(JSON.stringify(response) + '\n');
}
