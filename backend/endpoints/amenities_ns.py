from flask import request, jsonify, make_response
from flask_restx import fields, Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Amenity, User, Category, Media
from .images import save_image, delete_image_file

amenities_ns = Namespace("Amenities", description="Amenities management")

# Media serialization model
media_model = amenities_ns.model('Media', {
    'id': fields.Integer(readonly=True),
    'url': fields.String(),
    'amenity_id': fields.Integer(),
    'type': fields.String()
})

# Amenities serialization model
amenities_model = amenities_ns.model('Amenity', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'price_per_hour': fields.Float(required=True),
    'address': fields.String(required=True),
    'category_id': fields.Integer(required=True),
    'owner_id': fields.Integer(readonly=True)
})

@amenities_ns.route('')
class AmenitiesListResource(Resource):
    @amenities_ns.marshal_list_with(amenities_model)
    def get(self):
        """Lists all amenities"""
        return Amenity.query.all(), 200

    @jwt_required()
    @amenities_ns.expect(amenities_model)
    @amenities_ns.marshal_with(amenities_model)
    def post(self):
        """Create a new amenity"""
        data = request.form.to_dict()
        user_id = get_jwt_identity()
        category_name = data.get('category')
        category = Category.query.filter_by(name=category_name).first()

        new_amenity = Amenity(
            name=data.get('name'),
            description=data.get('description'),
            price_per_hour=data.get('price_per_hour'),
            address=data.get('address'),
            category_id=category.id,
            owner_id=user_id
        )
        new_amenity.save()

        images = request.files.getlist('images')
        for image in images:
            filename = save_image(image)
            if filename:
                media = Media(
                    url = filename,
                    type = 'image',
                    amenity_id = new_amenity.id
                )
                media.save()

        return new_amenity, 201


@amenities_ns.route('/<int:id>')
class AmenityResource(Resource):
    @jwt_required()
    @amenities_ns.marshal_with(amenities_model)
    def put(self, id):
        """Update an amenity"""
        amenity = Amenity.query.get_or_404(id)
        user_id = get_jwt_identity()

        if amenity.owner_id != user_id:
            amenity_ns.abort(403, message="Not authorized to update this amenity")

        # Update basic amenity data
        amenity_data = request.form.to_dict()
        amenity.update(
            name=amenity_data.get('name'),
            description=amenity_data.get('description'),
            price_per_hour=float(amenity_data.get('price_per_hour')) if amenity_data.get('price_per_hour') else None,
            address=amenity_data.get('address'),
            category_id=int(amenity_data.get('category_id')) if amenity_data.get('category_id') else None
        )

        # Handle image updates
        if 'delete_all_images' in request.form and request.form['delete_all_images'].lower() == 'true':
            # Delete all existing images
            for media in amenity.images:
                delete_image_file(media.file_path)
                media.delete()

        # Add new images
        images = request.files.getlist('images')
        for image in images:
            filename = save_image(image)
            if filename:
                media = Media(
                    url=filename,
                    amenity_id=amenity.id,
                    type='image'
                )
                media.save()

        return amenity, 200

            

    @jwt_required()
    def delete(self, id):
        """Delete an amenity"""
        amenity = Amenity.query.get_or_404(id)
        user_id = get_jwt_identity()

        if amenity.owner_id != user_id:
            amenity_ns.abort(403, message="Not authorized to delete this amenity")

        # Delete all associated images
        for media in amenity.images:
            delete_image_file(media.url)
            media.delete()

        # Delete the amenity
        amenity.delete()

        return {"message": "Amenity deleted successfully"}, 200